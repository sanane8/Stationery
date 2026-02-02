#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.db import connection

print("🔍 Checking Database Structure")
print("=" * 50)

with connection.cursor() as cursor:
    # Get table info
    cursor.execute("PRAGMA table_info(tracker_saleitem)")
    columns = cursor.fetchall()
    
    print("SaleItem table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check if there's any data
    cursor.execute("SELECT COUNT(*) FROM tracker_saleitem")
    count = cursor.fetchone()[0]
    print(f"\nTotal records: {count}")
    
    # Check if old item column still exists
    cursor.execute("PRAGMA table_info(tracker_saleitem)")
    columns = cursor.fetchall()
    has_item_column = any(col[1] == 'item_id' for col in columns)
    print(f"Has item_id column: {has_item_column}")
    
    if has_item_column:
        cursor.execute("SELECT item_id FROM tracker_saleitem LIMIT 5")
        item_ids = cursor.fetchall()
        print(f"Sample item_ids: {item_ids}")

print("\n" + "=" * 50)
