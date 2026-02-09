# Railway Deployment Guide

## Prerequisites
- Railway account
- GitHub repository with your code
- Railway CLI (optional)

## Quick Setup

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Railway deployment files"
git push origin main
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `Stationery` repository
4. Railway will automatically detect the Django app

### 3. Configure Environment Variables
In Railway dashboard, set these variables:

**Required:**
- `SECRET_KEY`: Generate a new secret key
- `DJANGO_SETTINGS_MODULE`: `stationery_tracker.production_settings`

**Optional (for email):**
- `EMAIL_HOST`: `smtp.gmail.com`
- `EMAIL_PORT`: `587`
- `EMAIL_HOST_USER`: Your Gmail
- `EMAIL_HOST_PASSWORD`: App password
- `DEFAULT_FROM_EMAIL`: Your email

**Optional (for SMS):**
- `AFRICASTALKING_USERNAME`: Your Africa's Talking username
- `AFRICASTALKING_API_KEY`: Your API key
- `AFRICASTALKING_SENDER_ID`: Your sender ID

### 4. Database Setup
Railway automatically provides PostgreSQL. The `DATABASE_URL` will be set automatically.

### 5. Deploy
- Railway will automatically build and deploy
- First deployment may take 5-10 minutes
- After deployment, visit your app at `https://your-app-name.railway.app`

## Files Created for Railway

### Core Files:
- `railway.toml` - Railway configuration
- `Procfile` - Process definition
- `nixpacks.toml` - Build configuration
- `Dockerfile` - Container definition
- `docker-compose.yml` - Local development
- `.env.example` - Environment variables template

### Scripts:
- `start.sh` - Startup script for Railway

## Post-Deployment Steps

### 1. Create Superuser
```bash
# In Railway dashboard, open console for your app
python manage.py createsuperuser
```

### 2. Verify Setup
- Visit `/admin/` to access Django admin
- Check that static files load correctly
- Test database connectivity

### 3. Custom Domain (Optional)
1. In Railway dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

## Troubleshooting

### Build Issues:
- Check `requirements.txt` for correct versions
- Verify `railway.toml` configuration
- Check build logs in Railway dashboard

### Runtime Issues:
- Verify environment variables
- Check database connection
- Review application logs

### Static Files Issues:
- Ensure `STATIC_ROOT` is set correctly
- Verify `collectstatic` runs during build
- Check Whitenoise middleware configuration

## Local Development with Docker

```bash
# Build and run locally
docker-compose up --build

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DJANGO_SETTINGS_MODULE` | Settings file path | Yes |
| `DATABASE_URL` | PostgreSQL connection | Auto |
| `RAILWAY_PUBLIC_DOMAIN` | Railway domain | Auto |
| `PORT` | Application port | Auto |
| `EMAIL_HOST` | SMTP server | No |
| `EMAIL_PORT` | SMTP port | No |
| `EMAIL_HOST_USER` | SMTP username | No |
| `EMAIL_HOST_PASSWORD` | SMTP password | No |
| `AFRICASTALKING_USERNAME` | SMS API username | No |
| `AFRICASTALKING_API_KEY` | SMS API key | No |

## Security Notes

1. **Secret Key**: Always use a strong, unique secret key
2. **Database**: Railway provides secure PostgreSQL automatically
3. **HTTPS**: Railway handles SSL automatically
4. **Environment Variables**: Never commit sensitive data to git
5. **Debug Mode**: Set to `False` in production

## Monitoring

- Railway provides built-in metrics and logs
- Check the "Logs" tab for real-time application logs
- Monitor "Metrics" for performance data
- Set up alerts for downtime or errors
