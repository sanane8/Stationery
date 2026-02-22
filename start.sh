#!/bin/bash

echo "=== DJANGO STARTUP ==="
cd /app

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating shop table if needed..."
python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
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
conn.commit()
conn.close()
print('Shop table created successfully')
"

echo "Running migrations..."
python manage.py migrate --fake-initial || echo "Migrations completed"

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:$PORT
