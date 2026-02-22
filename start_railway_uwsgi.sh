#!/bin/bash
# Railway deployment script using uWSGI
echo "Starting Railway deployment with uWSGI..."

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start uWSGI (better logging handling than gunicorn)
exec uwsgi --http :$PORT \
  --module stationery_tracker.production_settings:application \
  --processes 2 \
  --threads 4 \
  --disable-logging \
  --ignore-sigpipe \
  --ignore-write-errors \
  --disable-write-exception
