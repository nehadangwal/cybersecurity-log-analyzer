from . import db
from datetime import datetime

class LogAnalysis(db.Model):
    __tablename__ = 'log_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    total_entries = db.Column(db.Integer, default=0)
    anomaly_count = db.Column(db.Integer, default=0)
    summary = db.Column(db.Text)
    status = db.Column(db.String(50), default='processing')
    
    # Relationships
    log_entries = db.relationship('LogEntry', backref='analysis', lazy=True, cascade='all, delete-orphan')
    anomalies = db.relationship('Anomaly', backref='analysis', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_time': self.upload_time.isoformat(),
            'total_entries': self.total_entries,
            'anomaly_count': self.anomaly_count,
            'summary': self.summary,
            'status': self.status
        }

class LogEntry(db.Model):
    __tablename__ = 'log_entries'
    
    # 💥 FIX 1: RESTORE THE PRIMARY KEY 💥
    id = db.Column(db.Integer, primary_key=True)
    
    # Other necessary columns
    analysis_id = db.Column(db.Integer, db.ForeignKey('log_analyses.id'), nullable=False)
    timestamp = db.Column(db.String(50))
    source_ip = db.Column(db.String(50))
    destination_ip = db.Column(db.String(50), nullable=True)
    url = db.Column(db.Text)
    action = db.Column(db.String(10)) # GET, POST, etc.
    status_code = db.Column(db.String(10))
    bytes_sent = db.Column(db.Integer)
    user_agent = db.Column(db.Text)
    
    # 💥 FIX 2: raw_log column is defined here 💥
    raw_log = db.Column(db.Text)
    
    def to_dict(self):
        # FIX 3: to_dict method is now correct and includes raw_log
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'url': self.url,
            'action': self.action,
            'status_code': self.status_code,
            'bytes_sent': self.bytes_sent,
            'user_agent': self.user_agent,
            'raw_log': self.raw_log
        }

class Anomaly(db.Model):
    __tablename__ = 'anomalies'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('log_analyses.id'), nullable=False)
    log_entry_id = db.Column(db.Integer, db.ForeignKey('log_entries.id'))
    anomaly_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    severity = db.Column(db.String(20))
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    log_entry = db.relationship('LogEntry', backref='anomalies')
    
    def to_dict(self):
        # *** FIX APPLIED: Safely retrieve the source_ip via the relationship ***
        source_ip = self.log_entry.source_ip if self.log_entry else 'N/A'
        
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'log_entry_id': self.log_entry_id,
            'anomaly_type': self.anomaly_type,
            'description': self.description,
            'confidence_score': self.confidence_score,
            'severity': self.severity,
            'detected_at': self.detected_at.isoformat(),
            #'source_ip': source_ip, # <-- THIS IS THE MISSING FIELD
            # *** ADD THIS LINE ***
            'log_entry': self.log_entry.to_dict() if self.log_entry else None
        }