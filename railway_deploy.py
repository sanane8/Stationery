#!/usr/bin/env python3
"""
Railway Deployment Script with M-Pesa Integration
Railway offers free credits and can integrate with M-Pesa via payment gateways
"""

import os
import json

def create_railway_config():
    """Create Railway configuration files"""
    
    # Create railway.toml
    railway_config = """[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn stationery_tracker.wsgi:application"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10

[[services]]
name = "web"
source = "."
[services.variables]
PORT = "8080"
"""
    
    with open('railway.toml', 'w') as f:
        f.write(railway_config)
    
    print("✅ Created railway.toml")
    
    # Create M-Pesa integration guide
    mpesa_guide = """# M-Pesa Integration for Railway Deployment

## Option 1: Use Flutterwave (Recommended)
Flutterwave accepts M-Pesa and integrates well with Django.

### Steps:
1. Sign up at flutterwave.com
2. Get API keys
3. Install Django package: pip install flutterwave-sdk
4. Add to settings.py:
```python
FLUTTERWAVE_PUBLIC_KEY = os.getenv('FLUTTERWAVE_PUBLIC_KEY')
FLUTTERWAVE_SECRET_KEY = os.getenv('FLUTTERWAVE_SECRET_KEY')
FLUTTERWAVE_ENCRYPTION_KEY = os.getenv('FLUTTERWAVE_ENCRYPTION_KEY')
```

## Option 2: Direct M-Pesa API
Use Africa's Talking M-Pesa API (already configured in your app).

### Railway Deployment Steps:
1. Push to GitHub
2. Connect Railway to GitHub
3. Deploy automatically
4. Add environment variables in Railway dashboard
5. Configure domain

## Environment Variables for Railway:
- SECRET_KEY=your-secret-key
- DATABASE_URL=postgresql://...
- FLUTTERWAVE_PUBLIC_KEY=your-key
- FLUTTERWAVE_SECRET_KEY=your-key
- DEBUG=False
"""
    
    with open('MPESA_RAILWAY_GUIDE.md', 'w') as f:
        f.write(mpesa_guide)
    
    print("✅ Created MPESA_RAILWAY_GUIDE.md")

def create_railway_requirements():
    """Create requirements file optimized for Railway"""
    requirements = """Django==5.1.6
gunicorn==23.0.0
whitenoise==6.10.0
psycopg2-binary==2.9.10
django-cors-headers==4.7.0
django-humanize==0.1.2
flutterwave-sdk==1.0.8
python-decouple==3.8
"""
    
    with open('requirements_railway.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements_railway.txt")

if __name__ == "__main__":
    print("🚀 Preparing for Railway deployment with M-Pesa support...")
    create_railway_config()
    create_railway_requirements()
    print("\n🎉 Ready for Railway deployment!")
    print("📖 See MPESA_RAILWAY_GUIDE.md for M-Pesa integration")
