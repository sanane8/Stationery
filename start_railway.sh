#!/bin/bash
# Railway deployment script
echo "Starting Railway deployment..."

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn with configuration file
exec gunicorn stationery_tracker.production_settings:application --config gunicorn.conf.py
