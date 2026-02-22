#!/bin/bash
set -e

echo "Starting Django application on Railway..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --run-syncdb || echo "Migrations may have already run"

# Start Gunicorn server for production
echo "Starting Gunicorn server..."
exec gunicorn stationery_tracker.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --timeout 300 \
  --max-requests 1000 \
  --keep-alive 2 \
  --preload \
  --access-logfile - \
  --error-logfile - \
  --log-level info
