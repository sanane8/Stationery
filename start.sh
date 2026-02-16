#!/bin/bash
set -e

echo "Starting Django application on Render..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Start Gunicorn server with proper logging
echo "Starting Gunicorn server..."
exec gunicorn stationery_tracker.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --worker-class sync \
    --timeout 30 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload-app \
    --access-log - \
    --error-log - \
    --log-level info \
    --capture-output
