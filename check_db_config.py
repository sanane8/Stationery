#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.conf import settings
import os

print('=== Django Database Configuration ===')
print(f'Database NAME: {settings.DATABASES["default"]["NAME"]}')
print(f'Database ENGINE: {settings.DATABASES["default"]["ENGINE"]}')
print(f'Current working directory: {os.getcwd()}')
print(f'Settings module: {os.environ.get("DJANGO_SETTINGS_MODULE", "Not set")}')

# Check if the database file exists
db_path = settings.DATABASES["default"]["NAME"]
if os.path.exists(db_path):
    print(f'Database file exists: {db_path}')
    # Get file size
    size = os.path.getsize(db_path)
    print(f'Database file size: {size} bytes ({size/1024/1024:.2f} MB)')
else:
    print(f'Database file does NOT exist: {db_path}')

# Find all SQLite files in the project
print('\n=== All SQLite Files in Project ===')
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.sqlite3') or file.endswith('.db'):
            full_path = os.path.join(root, file)
            size = os.path.getsize(full_path) if os.path.exists(full_path) else 0
            print(f'  {full_path} ({size} bytes)')
