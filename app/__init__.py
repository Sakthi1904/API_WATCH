from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
from app.models import db, init_db
from app.email_alerts import init_mail
from app.monitor import APIMonitor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_db(app)
    init_mail(app)
    
    # Register blueprints/routes
    from app.routes import app as routes_blueprint
    app.register_blueprint(routes_blueprint)
    
    # Initialize API monitor
    api_monitor = APIMonitor(app)
    
    # Setup scheduler for periodic monitoring
    scheduler = BackgroundScheduler()
    
    def monitor_job():
        """Job to monitor all endpoints"""
        with app.app_context():
            try:
                api_monitor.monitor_all_endpoints()
                logger.info("Scheduled monitoring completed")
            except Exception as e:
                logger.error(f"Error in scheduled monitoring: {str(e)}")
    
    # Add monitoring job to scheduler
    monitoring_interval = app.config.get('MONITORING_INTERVAL', 60)
    scheduler.add_job(
        func=monitor_job,
        trigger="interval",
        seconds=monitoring_interval,
        id='api_monitoring_job',
        name='API Monitoring Job'
    )
    
    # Start scheduler
    try:
        scheduler.start()
        logger.info(f"Scheduler started with {monitoring_interval}s interval")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
    
    # Store scheduler in app context for cleanup
    app.scheduler = scheduler
    
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        """Shutdown scheduler when app context ends"""
        if hasattr(app, 'scheduler'):
            app.scheduler.shutdown()
    
    return app

# Create the app instance
app = create_app()

# Import routes after app creation to avoid circular imports
from app import routes
