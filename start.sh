#!/bin/bash
set -e

echo "Starting Django application on Railway..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --run-syncdb || echo "Migrations may have already run"

# Start Gunicorn server with explicit logging disabled
echo "Starting Gunicorn server..."
exec gunicorn stationery_tracker.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --timeout 300 \
  --max-requests 100 \
  --keep-alive 2 \
  --preload \
  --capture-output \
  --access-logfile - \
  --error-logfile - \
  --log-level warning \
  --no-access-logfile \
  --no-error-logfile
