# 🚀 New Railway Production Deployment Guide

This guide will help you deploy the Stationery Management System to a fresh Railway production environment.

---

## 🎯 Step 1: Create New Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"** 
3. Choose **"Deploy from GitHub repo"**
4. Select your `Stationery` repository
5. Wait for Railway to analyze the project

---

## 🎯 Step 2: Configure Web Service

### Service Settings
1. Click on your web service (created from GitHub)
2. Go to **Settings** tab
3. Set the following:

**Build Configuration:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: Leave empty (will use Procfile)
- **Root Directory**: Leave blank (manage.py is at root)

**Environment Variables:**
```
DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings
SECRET_KEY=django-insecure-your-unique-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*
RAILWAY_ENVIRONMENT=production
```

---

## 🎯 Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Wait for database to be created
4. Click on your web service → **Variables** tab
5. Click **"Add a variable reference"**
6. Select the PostgreSQL service (this sets DATABASE_URL)

---

## 🎯 Step 4: Update Configuration Files

### railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "bash start.sh"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/admin"
healthcheckTimeout = 100
healthcheckInterval = 30

[env]
PYTHON_VERSION = "3.11"
```

### Procfile
```
web: bash start.sh
```

---

## 🎯 Step 5: Set Release Command

In your web service → Settings:
1. Find **"Release Command"** section
2. Set to:
```bash
python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

---

## 🎯 Step 6: Generate Domain

1. Open your web service
2. Go to **Settings** → **Networking**
3. Click **"Generate domain"**
4. Copy your production URL (e.g., `https://stationery-production.up.railway.app`)

---

## 🎯 Step 7: Create Superuser

After deployment, create admin access:

**Option A - Railway CLI:**
```bash
railway run python manage.py createsuperuser
```

**Option B - Railway Dashboard:**
1. Go to your web service → **Console**
2. Run:
```bash
cd /app
python manage.py createsuperuser
```

---

## 🎯 Step 8: Configure CSRF Settings

Add your production domain to CSRF trusted origins in Railway Variables:
```
CSRF_TRUSTED_ORIGINS=https://your-domain.up.railway.app,https://*.up.railway.app
```

---

## 🎯 Step 9: Test Deployment

1. **Application URL**: `https://your-domain.up.railway.app`
2. **Admin URL**: `https://your-domain.up.railway.app/admin`
3. Test login with superuser credentials
4. Verify all features work:
   - Shop management
   - User roles
   - Sales tracking
   - Customer management
   - Static files loading

---

## 🔧 Troubleshooting

### Common Issues:

**Application Crashes:**
- Check deployment logs in Railway dashboard
- Verify DATABASE_URL is set correctly
- Ensure all environment variables are configured

**Static Files Not Loading:**
- Run `python manage.py collectstatic --noinput` manually
- Check WhiteNoise configuration in settings

**Database Errors:**
- Verify PostgreSQL service is linked
- Check DATABASE_URL format
- Run migrations manually if needed

**CSRF Issues:**
- Add domain to CSRF_TRUSTED_ORIGINS
- Verify ALLOWED_HOSTS includes Railway domains

---

## 🎉 Production Features

Your deployed system includes:

✅ **Multi-Shop Management**
- Complete shop isolation
- Role-based permissions
- Professional UI with animations

✅ **Production Infrastructure**
- PostgreSQL database with backups
- Automatic SSL certificates
- Auto-scaling capabilities
- Built-in monitoring

✅ **Security Features**
- CSRF protection
- Secure authentication
- Environment-based configuration

---

## 📱 Next Steps

1. **Create shops** via admin panel
2. **Add users** and assign to shops
3. **Configure SMS/email** if needed
4. **Set up custom domain** (optional)
5. **Monitor performance** via Railway dashboard

---

## 🎯 Quick Start Commands

```bash
# Deploy to Railway
git push origin main

# Check logs
railway logs --service your-service-name

# Run commands
railway run python manage.py createsuperuser
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
```

---

Your Stationery Management System is now ready for production use in Tanzania! 🌍

**Production URL**: Will be provided after Step 6
**Admin Access**: Will be available after Step 7
