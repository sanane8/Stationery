#!/bin/bash

echo "=== DJANGO STARTUP ==="
cd /app

echo "Creating shop table directly..."
sqlite3 db.sqlite3 <<EOF
CREATE TABLE IF NOT EXISTS tracker_shop (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO tracker_shop (id, name, is_active) VALUES (1, 'Default Shop', 1);
EOF

echo "Shop table created with sqlite3 command"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations with fake..."
python manage.py migrate --fake --noinput

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:$PORT
