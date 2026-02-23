#!/bin/bash

echo "=== DJANGO DEPLOYMENT STARTUP ==="
cd /app

echo "DATABASE_URL: $DATABASE_URL"

echo "Step 1: Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Step 2: Running database migrations..."
python manage.py migrate --noinput

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

# Create default shop with ID 1
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('INSERT OR IGNORE INTO tracker_shop (id, name, is_active) VALUES (1, \"Default Shop\", 1)')
    connection.commit()

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

echo "Step 5: Starting Django application..."
echo "✅ All setup complete, starting server..."
exec python manage.py runserver 0.0.0.0:$PORT
