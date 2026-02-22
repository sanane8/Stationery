#!/bin/bash

echo "=== DJANGO STARTUP ==="
cd /app

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating shop table if needed..."
python -c "
import os
import sqlite3
import django
from django.conf import settings

# Use the correct database path
db_path = settings.DATABASES['default']['NAME']
print(f'Database path: {db_path}')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create shop table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracker_shop (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insert default shop
cursor.execute('INSERT OR IGNORE INTO tracker_shop (id, name, is_active) VALUES (1, \"Default Shop\", 1)')

conn.commit()
conn.close()
print('Shop table created successfully')
"

echo "Running migrations with fake initial..."
python manage.py migrate --fake-initial --noinput || echo "Migrations completed"

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:$PORT
