#!/usr/bin/env python
"""
Migration fix for Railway deployment
Fixes foreign key constraint issues during migration
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')
django.setup()

from django.db import connection

def fix_foreign_key_constraints():
    """Fix foreign key constraints before migration"""
    
    print("🔧 Fixing foreign key constraints...")
    
    with connection.cursor() as cursor:
        # Check if shop table exists and has records
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracker_shop'")
        shop_table_exists = cursor.fetchone()
        
        if shop_table_exists:
            cursor.execute("SELECT COUNT(*) FROM tracker_shop")
            shop_count = cursor.fetchone()[0]
            
            if shop_count == 0:
                print("📝 Creating default shop...")
                cursor.execute("INSERT INTO tracker_shop (id, name, is_active, created_at, updated_at) VALUES (1, 'Default Shop', 1, datetime('now'), datetime('now'))")
                print("✅ Default shop created")
            else:
                print(f"✅ Shop table exists with {shop_count} records")
        else:
            print("⚠️  Shop table doesn't exist, will be created by migrations")
        
        # Fix stationery items with invalid shop_id
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracker_stationeryitem'")
        stationery_table_exists = cursor.fetchone()
        
        if stationery_table_exists:
            cursor.execute("UPDATE tracker_stationeryitem SET shop_id = 1 WHERE shop_id NOT IN (SELECT id FROM tracker_shop)")
            affected_rows = cursor.total_changes
            print(f"🔧 Fixed {affected_rows} stationery items with invalid shop references")
        
        # Fix products with invalid shop_id  
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracker_product'")
        product_table_exists = cursor.fetchone()
        
        if product_table_exists:
            cursor.execute("UPDATE tracker_product SET shop_id = 1 WHERE shop_id NOT IN (SELECT id FROM tracker_shop)")
            affected_rows = cursor.total_changes
            print(f"🔧 Fixed {affected_rows} products with invalid shop references")
    
    print("✅ Foreign key constraints fixed")

if __name__ == "__main__":
    try:
        fix_foreign_key_constraints()
        print("🎉 Migration fix completed successfully")
    except Exception as e:
        print(f"❌ Migration fix failed: {e}")
        sys.exit(1)
