# 🔧 Railway Environment Variables Fix

## 🚨 Issue Identified
Environment variables are causing web service crashes when added to Railway dashboard.

## 🎯 Solution Steps

### Step 1: Remove Problematic Environment Variables
In Railway dashboard → Stationery service → Variables:
1. **Remove** these environment variables:
   - `RAILWAY_ENVIRONMENT=production`
   - `SECRET_KEY=django-insecure-your-unique-secret-key-here`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=*`

### Step 2: Deploy with Minimal Configuration
```bash
railway up
```

### Step 3: Test Application
1. **Access**: https://stationery-production.up.railway.app
2. **Verify**: Application loads without crashes
3. **Test**: Basic functionality works

### Step 4: Add Variables One by One
Once stable, add environment variables gradually:

#### Add SECRET_KEY First
```
SECRET_KEY=django-insecure-stationery-tracker-production-key-12345
```

#### Test and Add DEBUG
```
SECRET_KEY=django-insecure-stationery-tracker-production-key-12345
DEBUG=False
```

#### Test and Add ALLOWED_HOSTS
```
SECRET_KEY=django-insecure-stationery-tracker-production-key-12345
DEBUG=False
ALLOWED_HOSTS=stationery-production.up.railway.app
```

## 🔍 Root Cause Analysis

### Why Environment Variables Cause Crashes
1. **ALLOWED_HOSTS=***: The wildcard may cause issues with Railway's internal routing
2. **DEBUG=False**: May conflict with Railway's debug settings
3. **SECRET_KEY Format**: Special characters in the key may cause parsing issues
4. **RAILWAY_ENVIRONMENT**: May conflict with Railway's internal environment

### Better Environment Variable Values
```
SECRET_KEY=django-insecure-stationery-tracker-production-key-12345
DEBUG=False
ALLOWED_HOSTS=stationery-production.up.railway.app
```

## 🚀 Alternative: Use Railway's Built-in Variables

Railway automatically provides these variables:
- `RAILWAY_ENVIRONMENT` (set by Railway)
- `RAILWAY_SERVICE_NAME` (set by Railway)
- `RAILWAY_PROJECT_NAME` (set by Railway)

Use Railway's built-in variables instead of custom ones.

## 🎯 Expected Results

### ✅ Stable Deployment
- **No Crashes**: Service runs continuously
- **Working Login**: CSRF protection works
- **Static Files**: Properly served
- **Database**: Connected and working

### ✅ Multi-Shop System
- **Shop Management**: Create and manage shops
- **User Roles**: Admin and shop_seller permissions
- **Data Isolation**: Complete shop-based separation
- **Professional UI**: Animations and auto-dismiss messages

## 📊 Final Configuration

### Minimal Working Config
```python
# settings.py - Environment variables with safe defaults
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-stationery-tracker-default-key-for-development')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Safe ALLOWED_HOSTS handling
allowed_hosts = os.environ.get('ALLOWED_HOSTS', 'stationery-production.up.railway.app')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(',') if host.strip()]
```

### Railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PYTHON_VERSION = "3.11"
```

## 🎉 Success Criteria

### Application is Stable When:
- ✅ **Loads**: https://stationery-production.up.railway.app loads
- ✅ **No Crashes**: Service runs for more than 5 minutes
- ✅ **Login Works**: Can access login page
- ✅ **Admin Access**: Can reach /admin
- ✅ **Static Files**: CSS and JS load properly

## 🚀 Next Steps

1. **Remove problematic environment variables**
2. **Deploy with minimal config**
3. **Test stability**
4. **Add variables one by one**
5. **Monitor for crashes**

This approach will identify which specific environment variable is causing the crashes.
