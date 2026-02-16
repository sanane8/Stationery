# Render Deployment Guide for Stationery Management System

## 🚀 Quick Setup

### 1. Prepare Your Repository
```bash
# Ensure your code is pushed to GitHub/GitLab
git add .
git commit -m "Configure for Render deployment"
git push origin main
```

### 2. Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub/GitLab
3. Create a new **Web Service**

### 3. Configure Web Service
```yaml
# Service Type: Web Service
# Environment: Python 3
# Build Command: pip install -r requirements.txt
# Start Command: bash start.sh
# Health Check Path: /
```

### 4. Database Setup
```yaml
# Add PostgreSQL Addon
# Plan: Free (or paid for production)
# Connection details will be available as environment variables
```

### 5. Environment Variables
Set these in Render dashboard:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=stationery_tracker.settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com

# Database (Render provides these automatically)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Additional Settings
PORT=10000
PYTHON_VERSION=3.11
```

### 6. Static Files
```python
# In settings.py
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

# For production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 🔧 Configuration Files

### render.yaml
```yaml
services:
  - type: web
    name: stationery-management
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "bash start.sh"
    healthCheckPath: /
    autoDeploy: true
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: stationery_tracker.settings
    addons:
      - type: postgres
        name: stationery-db
        plan: free
```

### gunicorn.conf.py
```python
# Render-specific configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 3
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### start.sh
```bash
#!/bin/bash
set -e
python manage.py collectstatic --noinput
python manage.py migrate
exec gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT
```

## 📋 Deployment Steps

### 1. Connect Repository
- Connect your GitHub/GitLab repository
- Select the branch to deploy (usually `main`)

### 2. Configure Service
- Choose **Web Service**
- Set **Runtime** to **Python 3**
- Configure build and start commands

### 3. Add Database
- Click **Add Database**
- Choose **PostgreSQL**
- Select plan (Free for development)

### 4. Set Environment Variables
- Go to **Environment** tab
- Add all required variables
- Render automatically provides `DATABASE_URL`

### 5. Deploy
- Click **Create Web Service**
- Render will automatically build and deploy
- Monitor logs for any issues

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/dbname
```

#### 2. Static Files Not Loading
```python
# Ensure in settings.py:
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

#### 3. Permission Denied
```bash
# Make start script executable
chmod +x start.sh
git add start.sh
git commit -m "Fix start script permissions"
```

#### 4. Build Failures
```bash
# Check requirements.txt
pip install -r requirements.txt --dry-run
```

### Debug Commands
```bash
# Check logs in Render dashboard
# View build logs
# View service logs

# Local testing
python manage.py check --deploy
python manage.py collectstatic --dry-run
```

## 🎯 Production Optimizations

### 1. Security
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-app.onrender.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

### 2. Performance
```python
# Database
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
}

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}
```

### 3. Monitoring
```python
# Logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## 📱 Post-Deployment

### 1. Create Superuser
```bash
# In Render shell
python manage.py createsuperuser
```

### 2. Load Initial Data
```bash
# If you have fixtures
python manage.py loaddata initial_data.json
```

### 3. Test Application
- Visit your app URL
- Test login functionality
- Verify database operations
- Check static files

## 🔄 Continuous Deployment

Render automatically deploys when you push to the connected branch. To control this:

```yaml
# In render.yaml
autoDeploy: true  # or false for manual deploys
```

## 📞 Support

- Render docs: [render.com/docs](https://render.com/docs)
- Django deployment: [docs.djangoproject.com](https://docs.djangoproject.com)
- Community support: [community.render.com](https://community.render.com)
