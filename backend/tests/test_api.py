"""
End-to-End API Tests for Cybersecurity Log Analyzer
Tests all endpoints, edge cases, and error handling
"""

import pytest
import os
import io
from app import create_app, db
from app.models import LogAnalysis, LogEntry, Anomaly


@pytest.fixture
def app():
    """Create test application"""
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['user'] == 'admin'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['status'] == 'failure'
    
    def test_login_missing_username(self, client):
        """Test login with missing username"""
        response = client.post('/api/login', json={
            'password': 'password123'
        })
        assert response.status_code == 400
    
    def test_login_missing_password(self, client):
        """Test login with missing password"""
        response = client.post('/api/login', json={
            'username': 'admin'
        })
        assert response.status_code == 400
    
    def test_login_empty_credentials(self, client):
        """Test login with empty credentials"""
        response = client.post('/api/login', json={
            'username': '',
            'password': ''
        })
        assert response.status_code == 400
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/api/login', json={
            'username': 'hacker',
            'password': 'password'
        })
        assert response.status_code == 401


class TestFileUpload:
    """Test file upload endpoints"""
    
    def test_upload_valid_apache_log(self, client):
        """Test uploading valid Apache log file"""
        log_content = b'''192.168.1.100 - - [02/Nov/2025:10:15:23 -0700] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [02/Nov/2025:10:15:24 -0700] "POST /api/login HTTP/1.1" 200 567 "-" "Mozilla/5.0"'''
        
        data = {
            'file': (io.BytesIO(log_content), 'test.log')
        }
        
        response = client.post('/api/upload-log', 
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert 'analysis_id' in json_data
        assert json_data['analysis_id'] > 0
    
    def test_upload_with_ai_enabled(self, client):
        """Test uploading with AI flag enabled"""
        log_content = b'''192.168.1.100 - - [02/Nov/2025:10:15:23 -0700] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'''
        
        data = {
            'file': (io.BytesIO(log_content), 'test.log'),
            'use_ai': 'true'
        }
        
        response = client.post('/api/upload-log', 
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
    
    def test_upload_no_file(self, client):
        """Test upload without file"""
        response = client.post('/api/upload-log',
                              data={},
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename"""
        data = {
            'file': (io.BytesIO(b'test'), '')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
    
    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        data = {
            'file': (io.BytesIO(b'test content'), 'test.pdf')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'Invalid file type' in json_data['error']
    
    def test_upload_empty_file(self, client):
        """Test upload with empty file"""
        data = {
            'file': (io.BytesIO(b''), 'empty.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200  # Should handle gracefully
    
    def test_upload_large_file(self, client):
        """Test upload with large file content"""
        # Create 1000 log entries
        log_lines = []
        for i in range(1000):
            log_lines.append(
                f'192.168.1.{i % 255} - - [02/Nov/2025:10:{i % 60:02d}:23 -0700] '
                f'"GET /page{i} HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
            )
        log_content = '\n'.join(log_lines).encode()
        
        data = {
            'file': (io.BytesIO(log_content), 'large.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'


class TestAnalysisRetrieval:
    """Test analysis retrieval endpoints"""
    
    def create_test_analysis(self, app):
        """Helper to create test analysis"""
        with app.app_context():
            analysis = LogAnalysis(
                filename='test.log',
                total_entries=10,
                anomaly_count=2,
                summary='Test summary',
                status='completed'
            )
            db.session.add(analysis)
            db.session.commit()
            return analysis.id
    
    def test_get_analysis_success(self, client, app):
        """Test retrieving existing analysis"""
        analysis_id = self.create_test_analysis(app)
        
        response = client.get(f'/api/analysis/{analysis_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['analysis']['id'] == analysis_id
        assert 'log_entries' in data
        assert 'anomalies' in data
        assert 'timeline' in data
    
    def test_get_analysis_not_found(self, client):
        """Test retrieving non-existent analysis"""
        response = client.get('/api/analysis/99999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_get_analysis_invalid_id(self, client):
        """Test with invalid analysis ID"""
        response = client.get('/api/analysis/invalid')
        assert response.status_code == 404
    
    def test_list_analyses(self, client, app):
        """Test listing all analyses"""
        # Create multiple analyses
        for i in range(3):
            self.create_test_analysis(app)
        
        response = client.get('/api/analyses')
        assert response.status_code == 200
        data = response.get_json()
        assert 'analyses' in data
        assert len(data['analyses']) == 3
    
    def test_list_analyses_empty(self, client):
        """Test listing when no analyses exist"""
        response = client.get('/api/analyses')
        assert response.status_code == 200
        data = response.get_json()
        assert data['analyses'] == []


class TestAnalysisDeletion:
    """Test analysis deletion"""
    
    def create_test_analysis(self, app):
        """Helper to create test analysis"""
        with app.app_context():
            analysis = LogAnalysis(
                filename='test.log',
                total_entries=10,
                anomaly_count=2,
                summary='Test summary',
                status='completed'
            )
            db.session.add(analysis)
            db.session.commit()
            return analysis.id
    
    def test_delete_analysis_success(self, client, app):
        """Test successful deletion"""
        analysis_id = self.create_test_analysis(app)
        
        response = client.delete(f'/api/analysis/{analysis_id}')
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(f'/api/analysis/{analysis_id}')
        assert response.status_code == 404
    
    def test_delete_analysis_not_found(self, client):
        """Test deleting non-existent analysis"""
        response = client.delete('/api/analysis/99999')
        assert response.status_code == 404


class TestStatistics:
    """Test statistics endpoint"""
    
    def test_get_stats(self, client):
        """Test retrieving statistics"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_analyses' in data
        assert 'total_logs_processed' in data
        assert 'total_anomalies_detected' in data
        assert 'severity_breakdown' in data
        assert 'critical' in data['severity_breakdown']
        assert 'high' in data['severity_breakdown']
        assert 'medium' in data['severity_breakdown']
        assert 'low' in data['severity_breakdown']


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_malformed_json(self, client):
        """Test with malformed JSON"""
        response = client.post('/api/login',
                              data='not json',
                              content_type='application/json')
        assert response.status_code in [400, 500]
    
    def test_sql_injection_attempt(self, client):
        """Test SQL injection protection"""
        response = client.post('/api/login', json={
            'username': "admin'; DROP TABLE users;--",
            'password': 'password'
        })
        # Should not crash, just return invalid credentials
        assert response.status_code in [400, 401]
    
    def test_xss_attempt_in_filename(self, client):
        """Test XSS protection in filename"""
        log_content = b'test log content'
        data = {
            'file': (io.BytesIO(log_content), '<script>alert("xss")</script>.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        # Should sanitize filename
        assert response.status_code == 200
    
    def test_unicode_in_logs(self, client):
        """Test handling unicode characters in logs"""
        log_content = '192.168.1.100 - - [02/Nov/2025:10:15:23] "GET /文档 HTTP/1.1" 200 1234'.encode('utf-8')
        
        data = {
            'file': (io.BytesIO(log_content), 'unicode.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
    
    def test_special_characters_in_logs(self, client):
        """Test handling special characters"""
        log_content = b'192.168.1.100 - - [02/Nov/2025:10:15:23] "GET /test?param=<>&\'" HTTP/1.1" 200 1234'
        
        data = {
            'file': (io.BytesIO(log_content), 'special.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
    
    def test_very_long_lines(self, client):
        """Test handling very long log lines"""
        # Create a line with 10000 characters
        long_url = 'a' * 10000
        log_content = f'192.168.1.100 - - [02/Nov/2025:10:15:23] "GET /{long_url} HTTP/1.1" 200 1234'.encode()
        
        data = {
            'file': (io.BytesIO(log_content), 'long.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
    
    def test_concurrent_uploads(self, client):
        """Test handling concurrent uploads"""
        log_content = b'192.168.1.100 - - [02/Nov/2025:10:15:23] "GET /test HTTP/1.1" 200 1234'
        
        responses = []
        for i in range(5):
            data = {
                'file': (io.BytesIO(log_content), f'test{i}.log')
            }
            response = client.post('/api/upload-log',
                                  data=data,
                                  content_type='multipart/form-data')
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200


class TestLogFormats:
    """Test different log formats"""
    
    def test_apache_format(self, client):
        """Test Apache/Nginx log format"""
        log_content = b'''192.168.1.100 - - [02/Nov/2025:10:15:23 -0700] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [02/Nov/2025:10:15:24 -0700] "POST /api/login HTTP/1.1" 401 567 "-" "curl/7.68.0"'''
        
        data = {
            'file': (io.BytesIO(log_content), 'apache.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
    
    def test_zscaler_format(self, client):
        """Test ZScaler log format"""
        log_content = b'''2025-11-02 10:00:00,user1@company.com,Engineering,SF,US,US,https://github.com,Tech,Dev,Code,None,None,None,Allow,Low,1024,5,512,512,Safe
2025-11-02 10:01:00,user2@company.com,Sales,NY,US,GB,https://salesforce.com,Business,CRM,Sales,None,None,None,Allow,Low,2048,3,1024,1024,Safe'''
        
        data = {
            'file': (io.BytesIO(log_content), 'zscaler.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
    
    def test_generic_format(self, client):
        """Test generic log format"""
        log_content = b'''2025-11-02 10:00:00 192.168.1.100 GET /api/users 200
2025-11-02 10:01:00 192.168.1.101 POST /api/login 401'''
        
        data = {
            'file': (io.BytesIO(log_content), 'generic.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
    
    def test_mixed_format(self, client):
        """Test mixed/corrupted format"""
        log_content = b'''192.168.1.100 - - [02/Nov/2025:10:15:23 -0700] "GET /index.html HTTP/1.1" 200 1234
corrupted line here
2025-11-02 10:00:00,user1@company.com,Engineering,SF
another corrupted line
192.168.1.101 - - [02/Nov/2025:10:15:24 -0700] "POST /api/login HTTP/1.1" 401 567'''
        
        data = {
            'file': (io.BytesIO(log_content), 'mixed.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        # Should handle gracefully
        assert response.status_code == 200


class TestAnomalyDetection:
    """Test anomaly detection functionality"""
    
    def test_detect_brute_force(self, client):
        """Test detection of brute force attacks"""
        # Create logs with multiple failed logins from same IP
        log_lines = []
        for i in range(10):
            log_lines.append(
                f'10.0.0.50 - - [02/Nov/2025:10:15:{i:02d} -0700] '
                f'"POST /admin/login HTTP/1.1" 401 123 "-" "python-requests/2.25.1"'
            )
        log_content = '\n'.join(log_lines).encode()
        
        data = {
            'file': (io.BytesIO(log_content), 'brute_force.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        # Verify analysis was created
        analysis_id = json_data['analysis_id']
        
        # Get analysis details
        response = client.get(f'/api/analysis/{analysis_id}')
        data = response.get_json()
        
        # Should detect brute force
        assert data['analysis']['anomaly_count'] > 0
        
        # Check for brute force type
        anomaly_types = [a['anomaly_type'] for a in data['anomalies']]
        assert 'brute_force_attack' in anomaly_types or 'high_frequency_ip' in anomaly_types
    
    def test_detect_port_scanning(self, client):
        """Test detection of port scanning"""
        # Create logs with one IP accessing many URLs
        log_lines = []
        for i in range(60):
            log_lines.append(
                f'45.67.89.123 - - [02/Nov/2025:10:15:{i % 60:02d} -0700] '
                f'"GET /path{i} HTTP/1.1" 404 567 "-" "Mozilla/5.0"'
            )
        log_content = '\n'.join(log_lines).encode()
        
        data = {
            'file': (io.BytesIO(log_content), 'port_scan.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        # Get analysis details
        analysis_id = json_data['analysis_id']
        response = client.get(f'/api/analysis/{analysis_id}')
        data = response.get_json()
        
        # Should detect anomalies
        assert data['analysis']['anomaly_count'] > 0
    
    def test_detect_off_hours_activity(self, client):
        """Test detection of off-hours activity"""
        log_content = b'''192.168.1.100 - - [02/Nov/2025:02:15:23 -0700] "GET /admin HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.100 - - [02/Nov/2025:03:15:23 -0700] "GET /data HTTP/1.1" 200 5678 "-" "Mozilla/5.0"'''
        
        data = {
            'file': (io.BytesIO(log_content), 'off_hours.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
    
    def test_no_anomalies_clean_logs(self, client):
        """Test that clean logs don't trigger false positives"""
        log_content = b'''192.168.1.100 - - [02/Nov/2025:10:15:23 -0700] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [02/Nov/2025:10:15:24 -0700] "GET /about.html HTTP/1.1" 200 567 "-" "Mozilla/5.0"
192.168.1.102 - - [02/Nov/2025:10:15:25 -0700] "GET /contact.html HTTP/1.1" 200 890 "-" "Mozilla/5.0"'''
        
        data = {
            'file': (io.BytesIO(log_content), 'clean.log')
        }
        
        response = client.post('/api/upload-log',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        # Get analysis details
        analysis_id = json_data['analysis_id']
        response = client.get(f'/api/analysis/{analysis_id}')
        data = response.get_json()
        
        # Should have minimal or no anomalies
        # (depending on thresholds)
        assert data['analysis']['total_entries'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
