# 🔧 Comprehensive CSRF 403 Fix Guide

## 🚨 Current Issue
Both local and Railway deployment showing:
```
Forbidden (Origin checking failed - https://stationery-production.up.railway.app does not match any trusted origins.)
```

## 🎯 Root Cause Analysis

### 1. Django 5.1 CSRF Changes
Django 5.1 has stricter CSRF origin checking by default.

### 2. Railway Domain Issues
Railway uses dynamic domains that may not match exactly.

### 3. Middleware Interference
Custom middleware might be interfering with CSRF tokens.

## ✅ Applied Fixes

### 1. Comprehensive CSRF Settings
```python
# Add CSRF trusted origins for Railway - direct approach
CSRF_TRUSTED_ORIGINS = [
    'https://stationery-production.up.railway.app',
    'https://*.up.railway.app',
    'https://railway.app',
    'http://stationery-production.up.railway.app',
    'http://*.up.railway.app',
    'http://railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
]

# Comprehensive CSRF settings for Railway and local development
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_ALLOW_CREDENTIALS = True
CSRF_USE_SESSIONS = False
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_SAMESITE = 'Lax'

# Also try environment variable approach
csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in csrf_origins.split(',') if origin.strip()])
```

### 2. Environment Variable Support
Add to Railway dashboard → Stationery service → Variables:
```
CSRF_TRUSTED_ORIGINS=https://stationery-production.up.railway.app,https://*.up.railway.app,https://railway.app
```

## 🧪 Testing Steps

### Step 1: Deploy Current Fix
```bash
railway up
```

### Step 2: Add Environment Variables
In Railway dashboard:
1. Go to Stationery service
2. Click "Variables" tab
3. Add: `CSRF_TRUSTED_ORIGINS=https://stationery-production.up.railway.app,https://*.up.railway.app,https://railway.app`
4. Save and redeploy

### Step 3: Test Login
1. Access: https://stationery-production.up.railway.app
2. Try login
3. Check for 403 errors

### Step 4: Check Logs
```bash
railway logs
```
Look for successful POST requests instead of 403 errors.

## 🔍 Alternative Solutions

### Option 1: Disable CSRF (Temporary)
```python
# Add to settings.py (ONLY for testing)
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
```

### Option 2: Use Django's Default
```python
# Remove all CSRF settings and let Django handle it
# This might work better with Django 5.1
```

### Option 3: Custom CSRF Decorator
```python
# In views.py
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    # Your login view code
```

### Option 4: Check Template CSRF Token
Ensure templates have:
```html
{% csrf_token %}
```

### Option 5: Check AJAX Requests
If using AJAX, ensure:
```javascript
// Include CSRF token in AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

fetch('/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data)
});
```

## 🚀 Production Considerations

### Security Settings for Production
```python
# For production with HTTPS
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'https://stationery-production.up.railway.app',
    'https://*.up.railway.app',
]
```

### Development Settings
```python
# For development
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

## 🎉 Success Criteria

### Login is Fixed When:
- ✅ **No 403 Error**: Login form submits successfully
- ✅ **Redirect Works**: User redirected after login
- ✅ **Session Active**: User remains logged in
- ✅ **Protected Pages**: Can access authenticated pages

### Local Development Works When:
- ✅ **No 403 Error**: Local login works
- ✅ **Same Settings**: Railway and local use same config
- ✅ **Debug Mode**: Can debug CSRF issues

## 📊 Next Steps

1. **Deploy Current Fix**: `railway up`
2. **Add Environment Variables**: In Railway dashboard
3. **Test Login**: Check both Railway and local
4. **Monitor Logs**: Look for successful POST requests
5. **Enable Security**: Once working, enable production security

**If still failing, try Option 1 (disable CSRF temporarily) to confirm that's the issue.**
