#!/usr/bin/env python3
"""
Production Setup Script for Stationery Management System
Local Deployment for Tanzania
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def check_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ manage.py not found. Run this script from the project root.")
        return False
    
    print("✅ Project directory confirmed")
    return True

def create_production_settings():
    """Create production settings file"""
    print("\n📝 Creating production settings...")
    
    settings_content = '''
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100', '0.0.0.0']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stationery_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stationery_tracker.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'stationery_db'),
        'USER': os.environ.get('DB_USER', 'stationery_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your-db-password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Email settings (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@stationery.co.tz')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'tracker': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Backup settings
BACKUP_DIR = BASE_DIR / 'backups'
BACKUP_SCHEDULE = '0 2 * * *'  # Daily at 2 AM
'''
    
    with open('stationery_tracker/production_settings.py', 'w') as f:
        f.write(settings_content)
    
    print("✅ Production settings created")
    return True

def create_gunicorn_config():
    """Create Gunicorn configuration"""
    print("\n📝 Creating Gunicorn configuration...")
    
    gunicorn_config = '''
# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
daemon = False
pidfile = "/var/run/gunicorn/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None
'''
    
    with open('gunicorn.conf.py', 'w') as f:
        f.write(gunicorn_config)
    
    print("✅ Gunicorn configuration created")
    return True

def create_systemd_service():
    """Create systemd service file"""
    print("\n📝 Creating systemd service...")
    
    current_dir = os.path.abspath('.')
    
    service_content = f'''[Unit]
Description=Stationery Management System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory={current_dir}
Environment=DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings
EnvironmentFile=/etc/environment
ExecStart=/usr/local/bin/gunicorn --config gunicorn.conf.py stationery_tracker.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
'''
    
    with open('stationery.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created")
    return True

def create_nginx_config():
    """Create Nginx configuration"""
    print("\n📝 Creating Nginx configuration...")
    
    nginx_config = '''
server {
    listen 80;
    server_name localhost 192.168.1.100;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost 192.168.1.100;
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/stationery.crt;
    ssl_certificate_key /etc/ssl/private/stationery.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Static files
    location /static/ {
        alias /home/user/stationery/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/user/stationery/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
'''
    
    with open('nginx-stationery.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Nginx configuration created")
    return True

def create_backup_script():
    """Create backup script"""
    print("\n📝 Creating backup script...")
    
    backup_script = '''#!/bin/bash
# Backup script for Stationery Management System

# Configuration
BACKUP_DIR="/home/user/stationery/backups"
DB_NAME="stationery_db"
DB_USER="stationery_user"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/stationery_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Database backup
echo "Creating database backup..."
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_FILE

# Compress backup
echo "Compressing backup..."
gzip $BACKUP_FILE

# Media files backup
echo "Backing up media files..."
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" /home/user/stationery/media/

# Upload to cloud (Google Drive - requires rclone)
if command -v rclone &> /dev/null; then
    echo "Uploading to cloud..."
    rclone copy $BACKUP_DIR gdrive:/stationery_backups/
fi

# Clean old backups (keep last 30 days)
echo "Cleaning old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
'''
    
    with open('backup.sh', 'w') as f:
        f.write(backup_script)
    
    # Make script executable
    os.chmod('backup.sh', 0o755)
    
    print("✅ Backup script created")
    return True

def create_deployment_checklist():
    """Create deployment checklist"""
    print("\n📝 Creating deployment checklist...")
    
    checklist = '''
# Stationery Management System - Deployment Checklist

## Pre-Deployment Checklist
- [ ] Ubuntu 22.04 LTS installed
- [ ] System updated (sudo apt update && sudo apt upgrade)
- [ ] Static IP configured (192.168.1.100)
- [ ] Firewall configured (UFW)
- [ ] UPS connected and tested
- [ ] Internet connection tested

## Software Installation
- [ ] Python 3.8+ installed
- [ ] PostgreSQL installed and configured
- [ ] Nginx installed
- [ ] Gunicorn installed
- [ ] SSL certificate generated
- [ ] Domain name configured (if applicable)

## Application Setup
- [ ] Virtual environment created
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] Database created and configured
- [ ] Production settings configured
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] Superuser created
- [ ] Systemd service enabled and started
- [ ] Nginx configured and started

## Security Configuration
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Database security configured
- [ ] Application security settings verified
- [ ] Backup script configured
- [ ] Log rotation configured

## Testing
- [ ] Application accessible via browser
- [ ] HTTPS working correctly
- [ ] User registration/login working
- [ ] Sales functionality working
- [ ] Debt management working
- [ ] Reports generating correctly
- [ ] Mobile responsiveness tested
- [ ] Print functionality tested

## Post-Deployment
- [ ] Monitoring configured
- [ ] Backup schedule configured
- [ ] Documentation provided
- [ ] Staff training completed
- [ ] Support contact information provided
- [ ] Maintenance schedule established

## Emergency Procedures
- [ ] Recovery procedures documented
- [ ] Contact information for support
- [ ] Backup restoration tested
- [ ] System monitoring alerts configured
'''
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    
    print("✅ Deployment checklist created")
    return True

def main():
    """Main setup function"""
    print("🚀 Stationery Management System - Production Setup")
    print("=" * 50)
    
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        return False
    
    print("\n📋 Creating production configuration files...")
    
    # Create all configuration files
    files_created = []
    
    if create_production_settings():
        files_created.append("production_settings.py")
    
    if create_gunicorn_config():
        files_created.append("gunicorn.conf.py")
    
    if create_systemd_service():
        files_created.append("stationery.service")
    
    if create_nginx_config():
        files_created.append("nginx-stationery.conf")
    
    if create_backup_script():
        files_created.append("backup.sh")
    
    if create_deployment_checklist():
        files_created.append("DEPLOYMENT_CHECKLIST.md")
    
    print(f"\n✅ Setup completed! Created {len(files_created)} files:")
    for file in files_created:
        print(f"   - {file}")
    
    print("\n📋 Next Steps:")
    print("1. Review the DEPLOYMENT_CHECKLIST.md")
    print("2. Install required software (PostgreSQL, Nginx, Gunicorn)")
    print("3. Configure your environment variables")
    print("4. Follow the deployment checklist step by step")
    print("5. Test the system thoroughly")
    
    print("\n📞 For technical support:")
    print("- Phone: +255 746 840 409")
    print("- Email: paul.sanane@gmail.com")
    
    return True

if __name__ == "__main__":
    main()
