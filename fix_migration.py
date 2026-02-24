#!/usr/bin/env python
"""
Migration fix for Railway deployment
Fixes foreign key constraints during migration
"""

import os
import sys
import django

# Add project directory to Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')
django.setup()

from django.db import connection

def fix_foreign_key_constraints():
    """Fix foreign key constraints before migration"""
    
    print(" Fixing foreign key constraints...")
    
    with connection.cursor() as cursor:
        # Check if shop table exists and create it if not
        if connection.vendor == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracker_shop (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    display_name VARCHAR(100),
                    description TEXT,
                    address TEXT,
                    phone VARCHAR(20),
                    email VARCHAR(254),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracker_shop (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    display_name VARCHAR(100),
                    description TEXT,
                    address TEXT,
                    phone VARCHAR(20),
                    email VARCHAR(254),
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Insert default shop
        if connection.vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO tracker_shop (id, name, display_name, is_active) 
                VALUES (1, 'stationery', 'Default Shop', TRUE) 
                ON CONFLICT (id) DO NOTHING
            """)
        else:
            cursor.execute("INSERT OR IGNORE INTO tracker_shop (id, name, display_name, is_active) VALUES (1, 'stationery', 'Default Shop', 1)")
        
        print(" Shop table created and populated")
        
        # Fix stationery items with invalid shop_id
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='tracker_stationeryitem'
        """ if connection.vendor != 'postgresql' else """
            SELECT tablename FROM pg_tables WHERE tablename='tracker_stationeryitem'
        """)
        stationery_table_exists = cursor.fetchone()
        
        if stationery_table_exists:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    UPDATE tracker_stationeryitem 
                    SET shop_id = 1 
                    WHERE shop_id NOT IN (SELECT id FROM tracker_shop)
                """)
            else:
                cursor.execute("""
                    UPDATE tracker_stationeryitem 
                    SET shop_id = 1 
                    WHERE shop_id NOT IN (SELECT id FROM tracker_shop)
                """)
            print(" Fixed stationery items with invalid shop references")
        
        # Fix products with invalid shop_id  
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='tracker_product'
        """ if connection.vendor != 'postgresql' else """
            SELECT tablename FROM pg_tables WHERE tablename='tracker_product'
        """)
        product_table_exists = cursor.fetchone()
        
        if product_table_exists:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    UPDATE tracker_product 
                    SET shop_id = 1 
                    WHERE shop_id NOT IN (SELECT id FROM tracker_shop)
                """)
            else:
                cursor.execute("""
                    UPDATE tracker_product 
                    SET shop_id = 1 
                    WHERE shop_id NOT IN (SELECT id FROM tracker_shop)
                """)
            print(" Fixed products with invalid shop references")
    
    print(" Foreign key constraints fixed")

if __name__ == "__main__":
    try:
        fix_foreign_key_constraints()
        print(" Migration fix completed successfully")
    except Exception as e:
        print(f" Migration fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
