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

echo "Step 2: Running database migrations directly..."
python manage.py migrate --noinput --fake-initial

echo "Step 3: Creating shop table first to fix foreign key constraints..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracker_shop (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('INSERT OR IGNORE INTO tracker_shop (id, name, is_active) VALUES (1, \"Default Shop\", 1)')
    connection.commit()
    print('✅ Shop table created and populated')
"

echo "Step 4: Running database migrations..."
python manage.py migrate --noinput --fake-initial

echo "Step 5: Creating superuser if needed..."
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

echo "Step 6: Verifying database integrity..."
python manage.py shell -c "
from tracker.models import Shop
try:
    shop = Shop.objects.get(id=1)
    print(f'✅ Shop ID 1 verified: {shop.name}')
except Shop.DoesNotExist:
    print('❌ Shop ID 1 missing')
"

echo "Step 7: Creating log directory..."
mkdir -p /var/log/gunicorn 2>/dev/null || echo "Log directory creation skipped"

echo "Step 8: Running debug tests..."
python debug_view.py

echo "Step 9: Starting Django application with Gunicorn..."
echo "✅ All setup complete, starting server..."
exec gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --log-level info --access-logfile - --error-logfile -
