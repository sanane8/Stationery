#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.db import connection
from tracker.models import ProductCategory, Category, Product

print("🔧 Fixing Category References with Raw SQL")
print("=" * 60)

# Disable foreign key constraints temporarily
with connection.cursor() as cursor:
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    try:
        # Get the category mappings
        files_folders_pc = ProductCategory.objects.get(name="Files & Folders")
        pvc_products_pc = ProductCategory.objects.get(name="PVC Products")
        
        files_folders_category = Category.objects.get(name="Files & Folders")
        pvc_products_category = Category.objects.get(name="PVC Products")
        
        print(f"📋 Mapping:")
        print(f"  Files & Folders: ProductCategory ID {files_folders_pc.id} -> Category ID {files_folders_category.id}")
        print(f"  PVC Products: ProductCategory ID {pvc_products_pc.id} -> Category ID {pvc_products_category.id}")
        
        # Update products with raw SQL
        cursor.execute(
            "UPDATE tracker_product SET category_id = %s WHERE category_id = %s",
            [files_folders_category.id, files_folders_pc.id]
        )
        files_updated = cursor.rowcount
        
        cursor.execute(
            "UPDATE tracker_product SET category_id = %s WHERE category_id = %s",
            [pvc_products_category.id, pvc_products_pc.id]
        )
        pvc_updated = cursor.rowcount
        
        print(f"\n✅ Updated {files_updated} Files & Folders products")
        print(f"✅ Updated {pvc_updated} PVC Products products")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"\n🎉 Category migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Re-enable foreign key constraints even if there's an error
        cursor.execute("PRAGMA foreign_keys = ON")

print("=" * 60)
