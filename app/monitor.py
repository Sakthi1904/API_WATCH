import requests
import time
from datetime import datetime, timedelta
from flask import current_app
from app.models import db, APIEndpoint, MonitoringResult, Alert
from app.email_alerts import send_alert_email, send_resolution_email

class APIMonitor:
    """API monitoring class that handles periodic checks of endpoints"""
    
    def __init__(self, app):
        self.app = app
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'APIWatch/1.0'
        })
    
    def check_endpoint(self, endpoint):
        """Check a single API endpoint and store results"""
        start_time = time.time()
        response_time = 0
        status_code = 0
        is_success = False
        error_message = None
        response_size = 0
        
        try:
            # Make the request
            response = self.session.request(
                method=endpoint.method,
                url=endpoint.url,
                headers=endpoint.headers,
                timeout=endpoint.timeout
            )
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            status_code = response.status_code
            response_size = len(response.content)
            
            # Determine if request was successful
            is_success = 200 <= status_code < 300
            
        except requests.exceptions.Timeout:
            error_message = "Request timeout"
            response_time = endpoint.timeout * 1000
        except requests.exceptions.ConnectionError:
            error_message = "Connection error"
        except requests.exceptions.RequestException as e:
            error_message = f"Request failed: {str(e)}"
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
        
        # Store the monitoring result
        result = MonitoringResult(
            endpoint_id=endpoint.id,
            response_time=response_time,
            status_code=status_code,
            is_success=is_success,
            error_message=error_message,
            response_size=response_size
        )
        
        with self.app.app_context():
            db.session.add(result)
            db.session.commit()
            
            # Check for alerts
            self.check_alerts(endpoint, result)
        
        return result
    
    def check_alerts(self, endpoint, result):
        """Check if alerts should be created based on monitoring result"""
        latency_threshold = current_app.config.get('LATENCY_THRESHOLD', 5000)
        
        # Check for API down (non-2xx status)
        if not result.is_success:
            self.create_alert(endpoint, 'down', 
                            f"API returned status {result.status_code}")
        
        # Check for high latency
        elif result.response_time > latency_threshold:
            self.create_alert(endpoint, 'high_latency',
                            f"Response time {result.response_time:.0f}ms exceeds threshold {latency_threshold}ms")
        
        # Check if previous alerts should be resolved
        self.check_resolve_alerts(endpoint, result)
    
    def create_alert(self, endpoint, alert_type, message):
        """Create a new alert if one doesn't already exist"""
        # Check if there's already an active alert of this type
        existing_alert = Alert.query.filter_by(
            endpoint_id=endpoint.id,
            alert_type=alert_type,
            is_resolved=False
        ).first()
        
        if not existing_alert:
            alert = Alert(
                endpoint_id=endpoint.id,
                alert_type=alert_type,
                message=message
            )
            
            with self.app.app_context():
                db.session.add(alert)
                db.session.commit()
                
                # Send email notification
                send_alert_email(alert, endpoint)
                
                current_app.logger.info(f"Created {alert_type} alert for {endpoint.name}")
    
    def check_resolve_alerts(self, endpoint, result):
        """Check if existing alerts should be resolved"""
        latency_threshold = current_app.config.get('LATENCY_THRESHOLD', 5000)
        
        # Get all active alerts for this endpoint
        active_alerts = Alert.query.filter_by(
            endpoint_id=endpoint.id,
            is_resolved=False
        ).all()
        
        for alert in active_alerts:
            should_resolve = False
            
            if alert.alert_type == 'down' and result.is_success:
                should_resolve = True
            elif alert.alert_type == 'high_latency' and result.response_time <= latency_threshold:
                should_resolve = True
            
            if should_resolve:
                alert.is_resolved = True
                alert.resolved_at = datetime.utcnow()
                
                with self.app.app_context():
                    db.session.commit()
                    send_resolution_email(alert, endpoint)
                    current_app.logger.info(f"Resolved {alert.alert_type} alert for {endpoint.name}")
    
    def monitor_all_endpoints(self):
        """Monitor all active endpoints"""
        with self.app.app_context():
            active_endpoints = APIEndpoint.query.filter_by(is_active=True).all()
            
            for endpoint in active_endpoints:
                try:
                    self.check_endpoint(endpoint)
                    current_app.logger.info(f"Monitored {endpoint.name}")
                except Exception as e:
                    current_app.logger.error(f"Error monitoring {endpoint.name}: {str(e)}")
    
    def get_endpoint_stats(self, endpoint_id, hours=24):
        """Get statistics for an endpoint over the specified time period"""
        with self.app.app_context():
            since = datetime.utcnow() - timedelta(hours=hours)
            
            results = MonitoringResult.query.filter(
                MonitoringResult.endpoint_id == endpoint_id,
                MonitoringResult.timestamp >= since
            ).order_by(MonitoringResult.timestamp).all()
            
            if not results:
                return {
                    'total_checks': 0,
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'min_response_time': 0,
                    'max_response_time': 0,
                    'error_count': 0
                }
            
            total_checks = len(results)
            successful_checks = sum(1 for r in results if r.is_success)
            success_rate = (successful_checks / total_checks) * 100
            
            response_times = [r.response_time for r in results if r.response_time > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            error_count = sum(1 for r in results if not r.is_success)
            
            return {
                'total_checks': total_checks,
                'success_rate': round(success_rate, 2),
                'avg_response_time': round(avg_response_time, 2),
                'min_response_time': round(min_response_time, 2),
                'max_response_time': round(max_response_time, 2),
                'error_count': error_count
            }
