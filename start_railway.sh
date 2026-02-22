#!/bin/bash
# Railway deployment script
echo "Starting Railway deployment..."

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Django development server for now (to bypass gunicorn logging issues)
exec python manage.py runserver 0.0.0.0:$PORT
