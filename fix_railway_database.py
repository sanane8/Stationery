#!/usr/bin/env python
"""
Fix Railway PostgreSQL database by adding missing columns
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

def fix_railway_database():
    """Add missing shop_id columns to Railway PostgreSQL database"""
    
    print("🔧 Fixing Railway PostgreSQL database...")
    
    with connection.cursor() as cursor:
        # Check database type
        db_vendor = connection.vendor
        print(f"📊 Database vendor: {db_vendor}")
        
        if db_vendor == 'postgresql':
            # Add shop_id column to tracker_sale table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_sale 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_sale")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_sale: {e}")
            
            # Add shop_id column to tracker_customer table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_customer 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_customer")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_customer: {e}")
            
            # Add shop_id column to tracker_category table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_category 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_category")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_category: {e}")
            
            # Add shop_id column to tracker_debt table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_debt 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_debt")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_debt: {e}")
            
            # Add shop_id column to tracker_expenditure table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_expenditure 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_expenditure")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_expenditure: {e}")
            
            # Add shop_id column to tracker_product table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_product 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_product")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_product: {e}")
            
            # Add shop_id column to tracker_productcategory table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_productcategory 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_productcategory")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_productcategory: {e}")
            
            # Add shop_id column to tracker_supplier table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_supplier 
                    ADD COLUMN IF NOT EXISTS shop_id INTEGER REFERENCES tracker_shop(id) DEFAULT 1
                """)
                print("✅ Added shop_id column to tracker_supplier")
            except Exception as e:
                print(f"⚠️  Error adding shop_id to tracker_supplier: {e}")
            
            # Add display_name column to tracker_shop table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_shop 
                    ADD COLUMN IF NOT EXISTS display_name VARCHAR(100) DEFAULT 'Default Shop'
                """)
                print("✅ Added display_name column to tracker_shop")
            except Exception as e:
                print(f"⚠️  Error adding display_name to tracker_shop: {e}")
            
            # Add assigned_shops and default_shop columns to tracker_userprofile table
            try:
                cursor.execute("""
                    ALTER TABLE tracker_userprofile 
                    ADD COLUMN IF NOT EXISTS default_shop_id INTEGER REFERENCES tracker_shop(id)
                """)
                print("✅ Added default_shop_id column to tracker_userprofile")
            except Exception as e:
                print(f"⚠️  Error adding default_shop_id to tracker_userprofile: {e}")
            
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
            
            # Ensure shop table has a record with id=1
            try:
                cursor.execute("""
                    INSERT INTO tracker_shop (id, name, display_name, is_active) 
                    VALUES (1, 'stationery', 'Default Shop', TRUE) 
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        display_name = EXCLUDED.display_name,
                        is_active = EXCLUDED.is_active
                """)
                print("✅ Ensured shop record with id=1 exists")
            except Exception as e:
                print(f"⚠️  Error creating default shop: {e}")
            
        else:
            print(f"❌ Unsupported database vendor: {db_vendor}")
            return False
    
    print("✅ Railway database fix completed")
    return True

if __name__ == "__main__":
    try:
        success = fix_railway_database()
        if success:
            print("🎉 Database fix completed successfully")
        else:
            print("💥 Database fix failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
