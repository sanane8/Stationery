#!/bin/bash
# Railway deployment script
echo "Starting Railway deployment..."

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn with completely disabled logging
exec gunicorn stationery_tracker.production_settings:application \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --timeout 300 \
  --access-logfile /dev/null \
  --error-logfile /dev/null \
  --log-level critical \
  --capture-output
