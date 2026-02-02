#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.db import connection
from tracker.models import SaleItem, StationeryItem, Product

print("🔄 Migrating Sale Items to New Structure")
print("=" * 60)

# Disable foreign key constraints temporarily
with connection.cursor() as cursor:
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    try:
        # Get all existing sale items
        old_sale_items = SaleItem.objects.all()
        print(f"Found {old_sale_items.count()} existing sale items to migrate")
        
        migrated_count = 0
        for sale_item in old_sale_items:
            # Get the old item reference
            old_item = sale_item.item
            
            # Set the new fields based on the old item
            sale_item.product_type = 'retail'
            sale_item.retail_item = old_item
            sale_item.wholesale_item = None
            
            # Save the changes
            sale_item.save()
            migrated_count += 1
            print(f"  ✅ Migrated: {old_item.name} -> retail_item")
        
        print(f"\n🎉 Successfully migrated {migrated_count} sale items!")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Re-enable foreign key constraints even if there's an error
        cursor.execute("PRAGMA foreign_keys = ON")

print("=" * 60)
