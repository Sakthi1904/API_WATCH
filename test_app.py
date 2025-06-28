#!/usr/bin/env python3
"""
Basic test script for APIWatch application
Run this to verify the application can start and basic functionality works
"""

import os
import sys
import requests
import time
from datetime import datetime

def test_flask_app():
    """Test if Flask app can start and respond"""
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        with app.app_context():
            from app.models import db
            print("✅ Database models loaded successfully")
            
            # Test database connection
            try:
                db.engine.execute("SELECT 1")
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if app is running"""
    try:
        # Wait a moment for app to start
        time.sleep(2)
        
        # Test dashboard endpoint
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard endpoint responding")
        else:
            print(f"❌ Dashboard endpoint returned {response.status_code}")
            return False
            
        # Test API stats endpoint
        response = requests.get("http://localhost:5000/api/dashboard/stats", timeout=5)
        if response.status_code == 200:
            print("✅ API stats endpoint responding")
            data = response.json()
            print(f"   - Total endpoints: {data.get('total_endpoints', 0)}")
            print(f"   - Active endpoints: {data.get('active_endpoints', 0)}")
        else:
            print(f"❌ API stats endpoint returned {response.status_code}")
            return False
            
        return True
    except requests.exceptions.ConnectionError:
        print("⚠️  App not running on localhost:5000 (this is normal if not started)")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔧 Environment Configuration:")
    
    # Check required environment variables
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'password' in var.lower() or 'key' in var.lower():
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (using default)")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 9:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} (requires 3.9+)")
        return False
    
    return True

def test_dependencies():
    """Test if required dependencies are installed"""
    print("\n📦 Dependencies Check:")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'psycopg2',
        'requests',
        'python_dotenv',
        'flask_mail',
        'apscheduler',
        'gunicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 APIWatch Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Dependencies", test_dependencies),
        ("Flask Application", test_flask_app),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("   docker-compose up")
        print("   or")
        print("   python -m flask run")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 