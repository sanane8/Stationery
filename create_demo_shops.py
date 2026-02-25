#!/usr/bin/env python
"""
Create demo shops for multi-shop functionality testing
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

def create_demo_shops():
    """Create demo shops for testing multi-shop functionality"""
    
    print("🔧 Creating demo shops...")
    
    with connection.cursor() as cursor:
        # Check database type
        db_vendor = connection.vendor
        print(f"📊 Database vendor: {db_vendor}")
        
        if db_vendor == 'postgresql':
            # Create demo shops
            demo_shops = [
                (1, 'stationery', 'Stationery Shop', True),  # Default shop - stationery
                (2, 'duka_la_vinywaji', 'Duka la Vinywaji', True),  # Enable duka la vinywaji
                (3, 'main_office', 'Main Office', True),
                (4, 'branch_a', 'Branch A - Downtown', True),
                (5, 'branch_b', 'Branch B - Uptown', True),
            ]
            
            for shop_id, name, display_name, is_active in demo_shops:
                try:
                    cursor.execute("""
                        INSERT INTO tracker_shop (id, name, display_name, is_active) 
                        VALUES (%s, %s, %s, %s) 
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            display_name = EXCLUDED.display_name,
                            is_active = EXCLUDED.is_active
                    """, [shop_id, name, display_name, is_active])
                    print(f"✅ Created/updated shop: {display_name}")
                except Exception as e:
                    print(f"⚠️  Error creating shop {name}: {e}")
            
            # Show all shops
            try:
                cursor.execute("SELECT id, name, display_name, is_active FROM tracker_shop ORDER BY id")
                shops = cursor.fetchall()
                print(f"\n📋 Available shops ({len(shops)} total):")
                for shop in shops:
                    status = "✅ Active" if shop[3] else "❌ Inactive"
                    print(f"   ID: {shop[0]} - {shop[2]} ({shop[1]}) - {status}")
            except Exception as e:
                print(f"⚠️  Error listing shops: {e}")
    
    print("✅ Demo shops creation completed")

if __name__ == "__main__":
    try:
        create_demo_shops()
        print("🎉 Demo shops setup completed successfully")
    except Exception as e:
        print(f"❌ Demo shops setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
