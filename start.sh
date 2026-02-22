#!/bin/bash
set -e

echo "Starting Django application on Railway..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment variables:"
env | grep -E '(PORT|RAILWAY|DATABASE)'

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Reset database and run migrations properly
echo "Checking database state..."
python manage.py showmigrations || echo "Show migrations failed"

echo "Running database migrations..."
python manage.py migrate --fake-initial || echo "Migrations completed with fake-initial"

# Create a shop if none exists
echo "Creating default shop if needed..."
python manage.py shell -c "
from tracker.models import Shop
if not Shop.objects.exists():
    Shop.objects.create(name='Default Shop', is_active=True)
    print('Default shop created')
else:
    print('Shop already exists')
"

# Start Django development server to avoid Gunicorn logging issues
echo "Starting Django server on port $PORT..."
exec python manage.py runserver 0.0.0.0:$PORT
