#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script for Stationery Management System
This script helps deploy the app to PythonAnywhere free tier.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def prepare_for_pythonanywhere():
    """Prepare the app for PythonAnywhere deployment"""
    print("🚀 Preparing Stationery Management System for PythonAnywhere")
    
    # Create requirements file for PythonAnywhere
    requirements = """Django==5.1.6
gunicorn==23.0.0
whitenoise==6.10.0
psycopg2-binary==2.9.10
python-decouple==3.8
django-cors-headers==4.7.0
django-humanize==0.1.2
"""
    
    with open('requirements_pythonanywhere.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements_pythonanywhere.txt")
    
    # Create PythonAnywhere-specific wsgi file
    wsgi_content = """import os
import sys
from pathlib import Path

# Add your project directory to the Python path
project_home = '/home/yourusername/Stationery'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')

# Configure Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""
    
    with open('pythonanywhere_wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Created pythonanywhere_wsgi.py")
    
    # Create deployment instructions
    instructions = """
# PythonAnywhere Deployment Instructions

## 1. Sign Up for Free Account
- Go to pythonanywhere.com
- Create free account (Bash console + Web app)

## 2. Upload Your Files
- Use the "Files" tab to upload your project
- Or use Git: git clone https://github.com/yourusername/Stationery

## 3. Set Up Virtual Environment
```bash
mkvirtualenv --python=python3.11 stationery
workon stationery
pip install -r requirements_pythonanywhere.txt
```

## 4. Configure Database
- Go to "Databases" tab
- Create PostgreSQL database
- Note connection details

## 5. Set Environment Variables
```bash
export SECRET_KEY='your-secret-key-here'
export DATABASE_URL='your-database-url'
export DEBUG=False
```

## 6. Configure Web App
- Go to "Web" tab
- Create new web app
- Select "Manual configuration"
- Python version: 3.11
- Point to your pythonanywhere_wsgi.py file
- Set virtualenv: /home/yourusername/.virtualenvs/stationery

## 7. Run Migrations
```bash
python manage.py migrate
```

## 8. Create Superuser
```bash
python manage.py createsuperuser
```

## 9. Reload Web App
- Click "Reload" button in Web tab

## 10. Access Your App
Your app will be available at: yourusername.pythonanywhere.com
"""
    
    with open('PYTHONANYWHERE_DEPLOYMENT.md', 'w') as f:
        f.write(instructions)
    
    print("✅ Created PYTHONANYWHERE_DEPLOYMENT.md")
    print("\n🎉 Ready for PythonAnywhere deployment!")
    print("📖 See PYTHONANYWHERE_DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    prepare_for_pythonanywhere()
