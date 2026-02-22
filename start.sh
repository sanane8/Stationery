#!/bin/bash

echo "=== DJANGO STARTUP ==="
cd /app

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput || echo "Migrations had issues"

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:$PORT
