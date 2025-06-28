# APIWatch - Cloud-Based API Monitoring Dashboard

APIWatch is a full-stack web application that provides real-time monitoring of third-party API performance and availability. Built with Flask, PostgreSQL, and modern web technologies, it offers comprehensive monitoring capabilities with email alerts and beautiful visualizations.

## 🚀 Features

- **Real-time API Monitoring**: Periodically checks API endpoints and tracks response times, status codes, and errors
- **Beautiful Dashboard**: Modern, responsive UI with Chart.js visualizations
- **Email Alerts**: Configurable email notifications for API downtime and performance issues
- **Database Storage**: PostgreSQL database for storing monitoring history and analytics
- **Docker Support**: Fully containerized application with Docker Compose
- **CI/CD Pipeline**: Automated testing, building, and deployment with GitHub Actions
- **AWS Deployment**: Ready for deployment on AWS EC2 with RDS

## 🏗️ Architecture

```
APIWatch/
├── app/                    # Flask application
│   ├── __init__.py        # App factory and configuration
│   ├── models.py          # Database models (SQLAlchemy)
│   ├── routes.py          # API routes and web endpoints
│   ├── monitor.py         # API monitoring logic
│   ├── email_alerts.py    # Email notification system
│   ├── templates/         # HTML templates
│   └── static/            # Static files (CSS, JS)
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Multi-container orchestration
└── .github/workflows/    # CI/CD pipelines
```

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **APScheduler**: Background task scheduling
- **Flask-Mail**: Email functionality

### Frontend
- **Bootstrap 5**: UI framework
- **Chart.js**: Data visualization
- **Font Awesome**: Icons
- **Vanilla JavaScript**: Interactive functionality

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD automation
- **AWS EC2**: Cloud deployment
- **AWS RDS**: Managed PostgreSQL database

## 📋 Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL (for local development)
- Git

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/apiwatch.git
   cd apiwatch
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   # Using Docker Compose (recommended)
   docker-compose up db -d
   
   # Or install PostgreSQL locally
   # Create database: apiwatch
   # Create user: apiwatch with password: password
   ```

5. **Run the application**
   ```bash
   # Development mode
   export FLASK_ENV=development
   flask run
   
   # Or using Docker Compose
   docker-compose up
   ```

6. **Access the dashboard**
   - Open http://localhost:5000 in your browser
   - Add your first API endpoint to monitor

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Web UI: http://localhost:5000
   - Database: localhost:5432

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key
FLASK_ENV=production

# Database Configuration
DATABASE_URL=postgresql://apiwatch:password@localhost:5432/apiwatch

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Monitoring Configuration
MONITORING_INTERVAL=60  # seconds
LATENCY_THRESHOLD=5000  # milliseconds
ALERT_EMAILS=admin@example.com,ops@example.com
```

### Email Setup (Gmail)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Use the App Password in your `.env` file

## 📊 Usage

### Adding API Endpoints

1. Navigate to the dashboard
2. Click "Add Endpoint" button
3. Fill in the endpoint details:
   - **Name**: Descriptive name for the endpoint
   - **URL**: Full URL to monitor
   - **Method**: HTTP method (GET, POST, etc.)
   - **Timeout**: Request timeout in seconds
   - **Active**: Enable/disable monitoring

### Monitoring Features

- **Real-time Monitoring**: Endpoints are checked automatically based on the configured interval
- **Response Time Tracking**: Measures and stores response times in milliseconds
- **Status Code Monitoring**: Tracks HTTP status codes and success rates
- **Error Detection**: Identifies connection errors, timeouts, and failed requests
- **Alert System**: Sends email notifications for:
  - API downtime (non-2xx status codes)
  - High latency (exceeds threshold)
  - Connection errors

### Dashboard Features

- **Overview Statistics**: Total endpoints, active endpoints, alerts, success rate
- **Endpoint Management**: Add, edit, delete, and test endpoints
- **Real-time Charts**: Response time trends and performance metrics
- **Alert Management**: View and resolve alerts
- **Historical Data**: 24-hour performance analytics

## 🚀 AWS Deployment

### Prerequisites

- AWS Account with EC2 and RDS access
- Domain name (optional)
- SSL certificate (recommended)

### Deployment Steps

1. **Launch EC2 Instance**
   ```bash
   # Use Ubuntu 20.04 LTS
   # Instance type: t3.medium or larger
   # Security group: Allow ports 22, 80, 443, 5000
   ```

2. **Set up RDS Database**
   ```bash
   # Create PostgreSQL RDS instance
   # Engine: PostgreSQL 13
   # Instance: db.t3.micro (for testing)
   # Enable public access for development
   ```

3. **Configure GitHub Secrets**
   Add these secrets to your GitHub repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `EC2_HOST`
   - `EC2_USERNAME`
   - `EC2_SSH_KEY`
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`

4. **Deploy via CI/CD**
   ```bash
   # Push to main branch triggers automatic deployment
   git push origin main
   ```

### Manual Deployment

1. **Connect to EC2 instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Install Docker and Docker Compose**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **Clone and deploy**
   ```bash
   git clone https://github.com/yourusername/apiwatch.git
   cd apiwatch
   cp env.example .env
   # Edit .env with production values
   docker-compose up -d
   ```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov flake8

# Run linting
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Run tests
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Coverage

The application includes tests for:
- Database models
- API endpoints
- Monitoring functionality
- Email alerts
- Configuration management

## 📈 Monitoring and Logging

### Application Logs

```bash
# View application logs
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web
```

### Database Monitoring

```bash
# Connect to database
docker-compose exec db psql -U apiwatch -d apiwatch

# View monitoring results
SELECT * FROM monitoring_results ORDER BY timestamp DESC LIMIT 10;
```

## 🔒 Security Considerations

- Change default database passwords
- Use strong SECRET_KEY
- Enable HTTPS in production
- Configure firewall rules
- Regular security updates
- Monitor access logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



**Made with ❤️ for reliable API monitoring**
