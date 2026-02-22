#!/bin/bash
set -e

echo "Starting Django application on Railway..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --run-syncdb || echo "Migrations may have already run"

# Start Django development server to avoid Gunicorn logging issues
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:$PORT
