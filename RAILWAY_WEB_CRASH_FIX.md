# 🚨 Railway Web Service (stationery) Crash Fix

## 🎯 Issue Identified
- **PostgreSQL Service**: ✅ Working fine
- **Web Service (stationery)**: ❌ Crashing repeatedly
- **Problem**: Web service configuration issues

## 🔧 Web Service Specific Fixes

### 1. Check Web Service Logs
In Railway dashboard:
1. Select "vibrant-sparkle" project
2. Click on "stationery" web service
3. View "Logs" tab
4. Look for specific error messages

### 2. Common Web Service Crash Causes

#### A. Memory Issues
**Problem**: Too many workers for Railway's memory limits
**Fix**: Further reduce workers and optimize memory

#### B. Database Connection Issues
**Problem**: Web service can't connect to PostgreSQL
**Fix**: Ensure proper database configuration

#### C. Static Files Issues
**Problem**: Missing static files directory
**Fix**: Create static files during startup

#### D. Django Settings Issues
**Problem**: Django configuration errors
**Fix**: Add better error handling

## 🚀 Immediate Fixes

### Fix 1: Reduce Workers to Minimum
Update Procfile with single worker:
```bash
web: gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --max-requests 500 --keep-alive 2
```

### Fix 2: Add Startup Script
Create startup script to handle static files:
```bash
#!/bin/bash
cd /app
python manage.py collectstatic --noinput
python manage.py migrate --run-syncdb
gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300
```

### Fix 3: Update Railway Configuration
Add health check and restart policy:
```toml
[[services]]
name = "web"

[services.web]
source = "."
healthcheck_path = "/"
healthcheck_grace_period = 30
healthcheck_interval = 30
healthcheck_timeout = 10
healthcheck_retries = 3

[services.web.deployment]
restart_policy_type = "ON_FAILURE"
restart_policy_max_retries = 10
```

## 🎯 Step-by-Step Fix

### Step 1: Update Procfile
Replace Procfile content with single worker configuration

### Step 2: Add Health Check
Update railway.toml with health check configuration

### Step 3: Redeploy Web Service
```bash
railway up
```

### Step 4: Monitor Web Service
Check logs to ensure web service stays running

## 🔍 Debugging Steps

### 1. Check Web Service Status
```bash
railway status
```

### 2. View Web Service Logs
```bash
railway logs
```

### 3. Test Web Service Manually
```bash
railway open
# In shell:
cd /app
python manage.py check --deploy
python manage.py runserver 0.0.0.0:8000
```

## 🎪 Expected Results

### ✅ Web Service Stable
- **Single Worker**: Reduced memory usage
- **Health Checks**: Railway monitors service health
- **Auto Restart**: Service restarts on failure
- **Better Logging**: Clear error messages

### ✅ Multi-Shop System Working
- **Shop Management**: Create and manage shops
- **User Roles**: Admin and shop_seller permissions
- **Shop Isolation**: Complete data separation
- **Professional UI**: Animations and auto-dismiss messages

## 🚀 Quick Fix Commands

### Update Procfile:
```bash
echo "web: gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --max-requests 500 --keep-alive 2" > Procfile
```

### Redeploy:
```bash
railway up
```

### Monitor:
```bash
railway logs
```

## 🎯 Focus on Web Service Only

The PostgreSQL service is working fine. We need to focus specifically on the "stationery" web service:

1. **Reduce Resource Usage**: Single worker
2. **Add Health Checks**: Railway monitoring
3. **Better Error Handling**: Clear logging
4. **Auto Restart**: Service recovery

Let's get your web service stable! 🚀
