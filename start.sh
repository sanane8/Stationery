#!/bin/bash
set -e

echo "Starting Django application on Railway..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --run-syncdb || echo "Migrations may have already run"

# Temporarily use Django development server to test if app works
echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:$PORT
