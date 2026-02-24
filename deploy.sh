#!/bin/bash

echo "=== DJANGO DEPLOYMENT STARTUP ==="
cd /app

echo "DATABASE_URL: $DATABASE_URL"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "DEBUG: $DEBUG"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set, using SQLite fallback"
    export DATABASE_URL="sqlite:///db.sqlite3"
fi

echo "Step 1: Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Step 2: Running database migrations..."
python manage.py migrate --noinput --fake-initial

echo "Step 3: Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth.models import User
from tracker.models import Shop

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')

# Verify shop exists
if not Shop.objects.exists():
    Shop.objects.create(name='Default Shop', is_active=True)
    print('✅ Default shop created')
else:
    print('✅ Shop already exists')

print(f'✅ Total shops: {Shop.objects.count()}')
"

echo "Step 4: Verifying database integrity..."
python manage.py shell -c "
from tracker.models import Shop
try:
    shop = Shop.objects.get(id=1)
    print(f'✅ Shop ID 1 verified: {shop.name}')
except Shop.DoesNotExist:
    print('❌ Shop ID 1 missing')
"

echo "Step 5: Creating log directory..."
mkdir -p /var/log/gunicorn 2>/dev/null || echo "Log directory creation skipped"

echo "Step 6: Starting Django application with Gunicorn..."
echo "✅ All setup complete, starting server..."
exec gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --log-level info --access-logfile - --error-logfile -
