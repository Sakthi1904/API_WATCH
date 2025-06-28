from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from app.models import APIEndpoint, MonitoringResult, Alert
from app.monitor import APIMonitor
from datetime import datetime, timedelta
import json

# Initialize API monitor
api_monitor = APIMonitor(app)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    # Get all endpoints
    endpoints = APIEndpoint.query.all()
    
    # Get recent alerts
    recent_alerts = Alert.query.filter_by(is_resolved=False).order_by(Alert.timestamp.desc()).limit(10).all()
    
    # Get overall stats
    total_endpoints = len(endpoints)
    active_endpoints = len([e for e in endpoints if e.is_active])
    active_alerts = len(recent_alerts)
    
    return render_template('dashboard.html',
                         endpoints=endpoints,
                         recent_alerts=recent_alerts,
                         total_endpoints=total_endpoints,
                         active_endpoints=active_endpoints,
                         active_alerts=active_alerts)

@app.route('/api/endpoints', methods=['GET'])
def get_endpoints():
    """Get all API endpoints"""
    endpoints = APIEndpoint.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'url': e.url,
        'method': e.method,
        'is_active': e.is_active,
        'created_at': e.created_at.isoformat()
    } for e in endpoints])

@app.route('/api/endpoints', methods=['POST'])
def add_endpoint():
    """Add a new API endpoint to monitor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('url'):
            return jsonify({'error': 'Name and URL are required'}), 400
        
        # Create new endpoint
        endpoint = APIEndpoint(
            name=data['name'],
            url=data['url'],
            method=data.get('method', 'GET'),
            headers=data.get('headers', {}),
            timeout=data.get('timeout', 30),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(endpoint)
        db.session.commit()
        
        return jsonify({
            'id': endpoint.id,
            'name': endpoint.name,
            'url': endpoint.url,
            'method': endpoint.method,
            'is_active': endpoint.is_active
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/endpoints/<int:endpoint_id>', methods=['PUT'])
def update_endpoint(endpoint_id):
    """Update an existing API endpoint"""
    try:
        endpoint = APIEndpoint.query.get_or_404(endpoint_id)
        data = request.get_json()
        
        if 'name' in data:
            endpoint.name = data['name']
        if 'url' in data:
            endpoint.url = data['url']
        if 'method' in data:
            endpoint.method = data['method']
        if 'headers' in data:
            endpoint.headers = data['headers']
        if 'timeout' in data:
            endpoint.timeout = data['timeout']
        if 'is_active' in data:
            endpoint.is_active = data['is_active']
        
        endpoint.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Endpoint updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/endpoints/<int:endpoint_id>', methods=['DELETE'])
def delete_endpoint(endpoint_id):
    """Delete an API endpoint"""
    try:
        endpoint = APIEndpoint.query.get_or_404(endpoint_id)
        db.session.delete(endpoint)
        db.session.commit()
        
        return jsonify({'message': 'Endpoint deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/endpoints/<int:endpoint_id>/stats')
def get_endpoint_stats(endpoint_id):
    """Get statistics for a specific endpoint"""
    try:
        hours = request.args.get('hours', 24, type=int)
        stats = api_monitor.get_endpoint_stats(endpoint_id, hours)
        
        # Get recent results for chart data
        since = datetime.utcnow() - timedelta(hours=hours)
        results = MonitoringResult.query.filter(
            MonitoringResult.endpoint_id == endpoint_id,
            MonitoringResult.timestamp >= since
        ).order_by(MonitoringResult.timestamp).all()
        
        chart_data = [{
            'timestamp': result.timestamp.isoformat(),
            'response_time': result.response_time,
            'status_code': result.status_code,
            'is_success': result.is_success
        } for result in results]
        
        return jsonify({
            'stats': stats,
            'chart_data': chart_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/endpoints/<int:endpoint_id>/test', methods=['POST'])
def test_endpoint(endpoint_id):
    """Test a specific endpoint immediately"""
    try:
        endpoint = APIEndpoint.query.get_or_404(endpoint_id)
        result = api_monitor.check_endpoint(endpoint)
        
        return jsonify({
            'response_time': result.response_time,
            'status_code': result.status_code,
            'is_success': result.is_success,
            'error_message': result.error_message,
            'timestamp': result.timestamp.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get all alerts"""
    resolved = request.args.get('resolved', 'false').lower() == 'true'
    alerts = Alert.query.filter_by(is_resolved=resolved).order_by(Alert.timestamp.desc()).all()
    
    return jsonify([{
        'id': a.id,
        'endpoint_name': a.endpoint.name,
        'alert_type': a.alert_type,
        'message': a.message,
        'timestamp': a.timestamp.isoformat(),
        'is_resolved': a.is_resolved,
        'resolved_at': a.resolved_at.isoformat() if a.resolved_at else None
    } for a in alerts])

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Mark an alert as resolved"""
    try:
        alert = Alert.query.get_or_404(alert_id)
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Alert resolved successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    try:
        # Get counts
        total_endpoints = APIEndpoint.query.count()
        active_endpoints = APIEndpoint.query.filter_by(is_active=True).count()
        active_alerts = Alert.query.filter_by(is_resolved=False).count()
        
        # Get recent monitoring activity (last 24 hours)
        since = datetime.utcnow() - timedelta(hours=24)
        recent_results = MonitoringResult.query.filter(
            MonitoringResult.timestamp >= since
        ).all()
        
        total_checks = len(recent_results)
        successful_checks = sum(1 for r in recent_results if r.is_success)
        success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0
        
        avg_response_time = 0
        if recent_results:
            response_times = [r.response_time for r in recent_results if r.response_time > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return jsonify({
            'total_endpoints': total_endpoints,
            'active_endpoints': active_endpoints,
            'active_alerts': active_alerts,
            'total_checks_24h': total_checks,
            'success_rate_24h': round(success_rate, 2),
            'avg_response_time_24h': round(avg_response_time, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """Start monitoring all endpoints"""
    try:
        api_monitor.monitor_all_endpoints()
        return jsonify({'message': 'Monitoring completed successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
