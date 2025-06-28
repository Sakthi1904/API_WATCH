-- APIWatch Database Initialization Script
-- This script sets up the initial database structure and permissions

-- Create database if it doesn't exist (this should be done by Docker)
-- CREATE DATABASE apiwatch;

-- Connect to the apiwatch database
\c apiwatch;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant necessary permissions to the apiwatch user
GRANT ALL PRIVILEGES ON DATABASE apiwatch TO apiwatch;
GRANT ALL PRIVILEGES ON SCHEMA public TO apiwatch;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO apiwatch;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO apiwatch;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO apiwatch;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO apiwatch;

-- Create indexes for better performance (these will be created by SQLAlchemy, but good to have)
-- The actual table creation is handled by Flask-SQLAlchemy

-- Create a function to clean up old monitoring data (optional)
CREATE OR REPLACE FUNCTION cleanup_old_monitoring_data(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM monitoring_results 
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get endpoint statistics
CREATE OR REPLACE FUNCTION get_endpoint_stats(endpoint_id_param INTEGER, hours_back INTEGER DEFAULT 24)
RETURNS TABLE(
    total_checks BIGINT,
    success_rate NUMERIC,
    avg_response_time NUMERIC,
    min_response_time NUMERIC,
    max_response_time NUMERIC,
    error_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_checks,
        ROUND(
            (COUNT(*) FILTER (WHERE is_success = true)::NUMERIC / COUNT(*)::NUMERIC) * 100, 2
        ) as success_rate,
        ROUND(AVG(response_time), 2) as avg_response_time,
        ROUND(MIN(response_time), 2) as min_response_time,
        ROUND(MAX(response_time), 2) as max_response_time,
        COUNT(*) FILTER (WHERE is_success = false)::BIGINT as error_count
    FROM monitoring_results 
    WHERE endpoint_id = endpoint_id_param 
    AND timestamp >= NOW() - INTERVAL '1 hour' * hours_back;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION cleanup_old_monitoring_data(INTEGER) TO apiwatch;
GRANT EXECUTE ON FUNCTION get_endpoint_stats(INTEGER, INTEGER) TO apiwatch;

-- Create a view for recent alerts
CREATE OR REPLACE VIEW recent_alerts AS
SELECT 
    a.id,
    a.endpoint_id,
    e.name as endpoint_name,
    e.url as endpoint_url,
    a.alert_type,
    a.message,
    a.timestamp,
    a.is_resolved,
    a.resolved_at,
    a.email_sent
FROM alerts a
JOIN api_endpoints e ON a.endpoint_id = e.id
ORDER BY a.timestamp DESC;

-- Grant permissions on the view
GRANT SELECT ON recent_alerts TO apiwatch;

-- Create a view for endpoint summary
CREATE OR REPLACE VIEW endpoint_summary AS
SELECT 
    e.id,
    e.name,
    e.url,
    e.method,
    e.is_active,
    e.created_at,
    COUNT(mr.id) as total_checks,
    COUNT(mr.id) FILTER (WHERE mr.is_success = true) as successful_checks,
    COUNT(mr.id) FILTER (WHERE mr.is_success = false) as failed_checks,
    ROUND(
        (COUNT(mr.id) FILTER (WHERE mr.is_success = true)::NUMERIC / 
         NULLIF(COUNT(mr.id), 0)::NUMERIC) * 100, 2
    ) as success_rate,
    ROUND(AVG(mr.response_time), 2) as avg_response_time,
    MAX(mr.timestamp) as last_check
FROM api_endpoints e
LEFT JOIN monitoring_results mr ON e.id = mr.endpoint_id
GROUP BY e.id, e.name, e.url, e.method, e.is_active, e.created_at;

-- Grant permissions on the view
GRANT SELECT ON endpoint_summary TO apiwatch;

-- Insert some sample data for testing (optional)
-- INSERT INTO api_endpoints (name, url, method, is_active) VALUES 
-- ('GitHub API', 'https://api.github.com', 'GET', true),
-- ('JSONPlaceholder', 'https://jsonplaceholder.typicode.com/posts/1', 'GET', true),
-- ('HTTPBin', 'https://httpbin.org/status/200', 'GET', true);

COMMIT; 