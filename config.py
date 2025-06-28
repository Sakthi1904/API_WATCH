import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://apiwatch:password@localhost:5432/apiwatch'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Monitoring configuration
    MONITORING_INTERVAL = int(os.environ.get('MONITORING_INTERVAL', 60))  # seconds
    LATENCY_THRESHOLD = int(os.environ.get('LATENCY_THRESHOLD', 5000))  # milliseconds
    ALERT_EMAILS = os.environ.get('ALERT_EMAILS', '').split(',')  # comma-separated emails
    
    # API monitoring settings
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))  # seconds
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 