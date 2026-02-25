#!/usr/bin/env python
"""
Quick fix for Railway PostgreSQL database - add missing shop_id columns
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

def quick_fix():
    """Quick fix for missing shop_id columns"""
    
    print("🔧 Quick database fix for Railway...")
    
    with connection.cursor() as cursor:
        # Check database type
        db_vendor = connection.vendor
        print(f"📊 Database vendor: {db_vendor}")
        
        if db_vendor == 'postgresql':
            # Add missing shop_id columns
            tables_to_fix = [
                'tracker_stationeryitem',
                'tracker_sale', 
                'tracker_customer',
                'tracker_category',
                'tracker_debt',
                'tracker_expenditure',
                'tracker_product',
                'tracker_productcategory',
                'tracker_supplier'
            ]
            
            for table in tables_to_fix:
                try:
                    cursor.execute(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN IF NOT EXISTS shop_id INTEGER 
                    """)
                    print(f"✅ Added shop_id to {table}")
                except Exception as e:
                    print(f"⚠️  Error adding shop_id to {table}: {e}")
            
            # Add display_name to shop table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_shop 
                    ADD COLUMN IF NOT EXISTS display_name VARCHAR(100) DEFAULT 'Default Shop'
                """)
                print("✅ Added display_name to tracker_shop")
            except Exception as e:
                print(f"⚠️  Error adding display_name: {e}")
            
            # Add created_by_id to tracker_debt table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_debt 
                    ADD COLUMN IF NOT EXISTS created_by_id INTEGER
                """)
                print("✅ Added created_by_id to tracker_debt")
            except Exception as e:
                print(f"⚠️  Error adding created_by_id to tracker_debt: {e}")
            
            # Create tracker_userprofile table if it doesn't exist
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tracker_userprofile (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                        role VARCHAR(20) DEFAULT 'shop_seller',
                        phone VARCHAR(20) DEFAULT '',
                        default_shop_id INTEGER REFERENCES tracker_shop(id) ON DELETE SET NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Created tracker_userprofile table")
            except Exception as e:
                print(f"⚠️  Error creating tracker_userprofile table: {e}")
            
            # Create the many-to-many table for assigned_shops
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tracker_userprofile_assigned_shops (
                        id SERIAL PRIMARY KEY,
                        userprofile_id INTEGER NOT NULL REFERENCES tracker_userprofile(id) ON DELETE CASCADE,
                        shop_id INTEGER NOT NULL REFERENCES tracker_shop(id) ON DELETE CASCADE,
                        UNIQUE(userprofile_id, shop_id)
                    )
                """)
                print("✅ Created tracker_userprofile_assigned_shops table")
            except Exception as e:
                print(f"⚠️  Error creating assigned_shops table: {e}")
            
            # Ensure shop table has a record
            try:
                cursor.execute("""
                    INSERT INTO tracker_shop (id, name, display_name, is_active) 
                    VALUES (1, 'Default Shop', 'Default Shop', TRUE) 
                    ON CONFLICT (id) DO NOTHING
                """)
                print("✅ Ensured default shop exists")
            except Exception as e:
                print(f"⚠️  Error creating default shop: {e}")
            
            # Add missing columns to tracker_shop table
            shop_columns = [
                ("description", "TEXT DEFAULT ''"),
                ("address", "TEXT DEFAULT ''"),
                ("phone", "VARCHAR(20) DEFAULT ''"),
                ("email", "VARCHAR(254) DEFAULT ''"),
                ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ]
            
            for column_name, column_def in shop_columns:
                try:
                    cursor.execute(f"""
                        ALTER TABLE tracker_shop 
                        ADD COLUMN IF NOT EXISTS {column_name} {column_def}
                    """)
                    print(f"✅ Added {column_name} to tracker_shop")
                except Exception as e:
                    print(f"⚠️  Error adding {column_name} to tracker_shop: {e}")
            
            # Update all records to use shop_id = 1
            for table in tables_to_fix:
                try:
                    cursor.execute(f"""
                        UPDATE {table} 
                        SET shop_id = 1 
                        WHERE shop_id IS NULL
                    """)
                    print(f"✅ Updated {table} records to use shop_id = 1")
                except Exception as e:
                    print(f"⚠️  Error updating {table}: {e}")
    
    print("✅ Quick database fix completed")

if __name__ == "__main__":
    try:
        quick_fix()
        print("🎉 Quick fix completed successfully")
    except Exception as e:
        print(f"❌ Quick fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
