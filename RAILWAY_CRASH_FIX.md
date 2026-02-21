# Railway Web Service Crash Fix

## 🚨 Issue Identified
Web service is crashing after deployment. Common causes and solutions:

## 🔧 Common Railway Crash Issues & Solutions

### Issue 1: Missing Environment Variables
**Problem**: Required environment variables not set
**Solution**: Set these in Railway dashboard:
```
RAILWAY_ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-railway-url.railway.app
```

### Issue 2: Database Connection Issues
**Problem**: Can't connect to PostgreSQL
**Solution**: Check DATABASE_URL is properly set by Railway

### Issue 3: Port Configuration
**Problem**: Gunicorn trying to use wrong port
**Solution**: Update Procfile:
```
web: gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

### Issue 4: Static Files Issues
**Problem**: Static files collection failing
**Solution**: Ensure STATIC_ROOT is configured correctly

### Issue 5: Django Settings Issues
**Problem**: Django settings causing startup failure
**Solution**: Check for syntax errors or missing imports

## 🚀 Quick Fix Steps

### Step 1: Check Railway Logs
1. Go to Railway dashboard
2. Click your web service
3. View "Logs" tab
4. Look for specific error messages

### Step 2: Set Environment Variables
In Railway dashboard, add:
```
RAILWAY_ENVIRONMENT=production
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*
```

### Step 3: Update Procfile
Replace your Procfile content with:
```
web: gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

### Step 4: Redeploy
```bash
railway up
```

## 🔍 Debugging Commands

### Check Application Status
```bash
# Connect to Railway shell
railway open

# Test Django settings
cd /app
python manage.py check --deploy

# Test database connection
python manage.py dbshell
```

### Check Environment Variables
```bash
# In Railway shell
echo $DATABASE_URL
echo $SECRET_KEY
echo $RAILWAY_ENVIRONMENT
```

## 🎯 Most Likely Issues

### 1. Missing ALLOWED_HOSTS
Django needs to know which hosts are allowed:
```python
# In settings.py
ALLOWED_HOSTS = ['*']  # For development
# Or specific hosts for production
ALLOWED_HOSTS = ['your-app.railway.app']
```

### 2. SECRET_KEY Not Set
Django requires a secret key:
```python
# In settings.py
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')
```

### 3. Database Connection
Ensure PostgreSQL is properly connected:
```python
# Database configuration should handle Railway properly
```

## 🚀 Emergency Fix

If you need to fix quickly:

1. **Update settings.py** with proper environment handling
2. **Set environment variables** in Railway dashboard
3. **Update Procfile** with correct gunicorn settings
4. **Redeploy with `railway up`**

## 🎪 After Fix

Once fixed, your multi-shop system will have:
- ✅ **Shop Management**: Multiple shops with complete isolation
- ✅ **User Roles**: Admin and shop_seller permissions
- ✅ **Professional UI**: Animations and auto-dismiss messages
- ✅ **Shop Switching**: Seamless transitions between shops
- ✅ **Data Security**: Complete shop-based access control

## 📞 Get Help

If issues persist:
1. **Check Railway logs** for specific error messages
2. **Verify environment variables** are set correctly
3. **Test locally** with same configuration
4. **Contact Railway support** if infrastructure issues

Let's get your multi-shop system running! 🚀
