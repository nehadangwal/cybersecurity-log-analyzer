"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def test_data_dir():
    """Return path to test data directory"""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture(scope='session')
def sample_apache_log():
    """Sample Apache log content"""
    return '''192.168.1.100 - - [02/Nov/2025:10:15:23 -0700] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [02/Nov/2025:10:15:24 -0700] "POST /api/login HTTP/1.1" 200 567 "-" "Mozilla/5.0"
192.168.1.102 - - [02/Nov/2025:10:15:25 -0700] "GET /admin/dashboard HTTP/1.1" 403 234 "-" "curl/7.68.0"
10.0.0.50 - - [02/Nov/2025:10:15:26 -0700] "POST /admin/login HTTP/1.1" 401 123 "-" "python-requests/2.25.1"
10.0.0.50 - - [02/Nov/2025:10:15:27 -0700] "POST /admin/login HTTP/1.1" 401 123 "-" "python-requests/2.25.1"
10.0.0.50 - - [02/Nov/2025:10:15:28 -0700] "POST /admin/login HTTP/1.1" 401 123 "-" "python-requests/2.25.1"'''

@pytest.fixture(scope='session')
def sample_zscaler_log():
    """Sample ZScaler log content"""
    return '''2025-11-02 10:00:00,user1@company.com,Engineering,SF,US,US,https://github.com,Tech,Dev,Code,None,None,None,Allow,Low,1024,5,512,512,Safe
2025-11-02 10:01:00,user2@company.com,Sales,NY,US,GB,https://salesforce.com,Business,CRM,Sales,None,None,None,Allow,Low,2048,3,1024,1024,Safe
2025-11-02 10:02:00,hacker@evil.com,Unknown,Unknown,RU,US,https://company.com/admin,Tech,Web,Admin,None,None,None,Block,High,0,85,0,0,Unsafe'''