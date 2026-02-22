#!/bin/bash

echo "=== DJANGO STARTUP ==="
cd /app

echo "DATABASE_URL: $DATABASE_URL"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth.models import User
from tracker.models import Shop
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')

if not Shop.objects.exists():
    Shop.objects.create(name='Default Shop', is_active=True)
    print('Default shop created')
else:
    print('Shop already exists')
"

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:$PORT
