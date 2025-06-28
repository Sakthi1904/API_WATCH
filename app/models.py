from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class APIEndpoint(db.Model):
    """Model for storing API endpoints to monitor"""
    __tablename__ = 'api_endpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    method = db.Column(db.String(10), default='GET')
    headers = db.Column(db.JSON, default={})
    timeout = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with monitoring results
    results = db.relationship('MonitoringResult', backref='endpoint', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<APIEndpoint {self.name}: {self.url}>'

class MonitoringResult(db.Model):
    """Model for storing API monitoring results"""
    __tablename__ = 'monitoring_results'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('api_endpoints.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    response_time = db.Column(db.Float, nullable=False)  # in milliseconds
    status_code = db.Column(db.Integer, nullable=False)
    is_success = db.Column(db.Boolean, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    response_size = db.Column(db.Integer, nullable=True)  # in bytes
    
    def __repr__(self):
        return f'<MonitoringResult {self.endpoint_id}: {self.status_code} ({self.response_time}ms)>'

class Alert(db.Model):
    """Model for storing alerts"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('api_endpoints.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'down', 'high_latency', 'error'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    email_sent = db.Column(db.Boolean, default=False)
    
    # Relationship with endpoint
    endpoint = db.relationship('APIEndpoint', backref='alerts')
    
    def __repr__(self):
        return f'<Alert {self.alert_type}: {self.message}>'

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
