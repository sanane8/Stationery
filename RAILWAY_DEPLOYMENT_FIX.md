# Railway Deployment Fix Guide

## Issues Fixed
1. **Database Connection Issue**: The "psql: command not found" error was because Railway doesn't have psql client installed, but Django can still connect using psycopg2-binary
2. **403 Forbidden Error**: Caused by CSRF configuration issues and missing environment variables

## Required Environment Variables in Railway

Set these in your Railway project settings:

### Core Django Settings
```
SECRET_KEY=your-very-secret-key-here-change-this-in-production
DEBUG=False
DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings
ALLOWED_HOSTS=your-domain.up.railway.app
```

### Database (Railway provides this automatically)
```
DATABASE_URL=postgresql://username:password@host:port/database
```

### Railway Specific
```
RAILWAY_PUBLIC_DOMAIN=your-app-name.up.railway.app
PORT=8000
```

## Steps to Deploy

1. **Push your changes to Git** (Railway will auto-deploy)

2. **Set Environment Variables in Railway**:
   - Go to your Railway project
   - Click on your service
   - Go to "Variables" tab
   - Add the environment variables above

3. **Add PostgreSQL Database**:
   - In Railway, click "New Service"
   - Select "PostgreSQL"
   - Railway will automatically provide DATABASE_URL

4. **Redeploy**:
   - Railway will automatically redeploy when you push changes
   - Or manually redeploy from the dashboard

## What Was Fixed

### 1. Database Configuration
- Fixed database URL detection in production_settings.py
- Added proper connection pooling and health checks
- Railway automatically provides DATABASE_URL

### 2. CSRF Configuration
- Secured CSRF cookies for production
- Added proper trusted origins
- Fixed ALLOWED_HOSTS configuration

### 3. Production Settings
- Created proper production settings module
- Added missing middleware and context processors
- Secured session and CSRF cookies

### 4. Deployment Configuration
- Updated railway.toml to use production settings
- Added automatic database migrations
- Set proper DJANGO_SETTINGS_MODULE

## Troubleshooting

If you still get 403 errors:
1. Check that SECRET_KEY is set and unique
2. Verify ALLOWED_HOSTS includes your Railway domain
3. Ensure CSRF_TRUSTED_ORIGINS includes your HTTPS domain
4. Make sure you're accessing the site via HTTPS

If database issues persist:
1. Verify DATABASE_URL is set correctly
2. Check that PostgreSQL service is running in Railway
3. Ensure migrations run successfully

## Verification Commands

After deployment, you can check:
- Railway logs for any errors
- Database connection in Django admin
- Login functionality should work without 403 errors
