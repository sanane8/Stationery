#!/usr/bin/env python
"""
Fix migration history inconsistency
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

def fix_migration_history():
    """Fix migration history by removing problematic migrations"""
    
    print("🔧 Fixing migration history...")
    
    with connection.cursor() as cursor:
        # Remove migrations that were applied out of order
        migrations_to_remove = [
            '0014_sale_shop',
            '0015_customer_shop', 
            '0016_category_shop_debt_shop_expenditure_shop_and_more',
            '0017_fix_debt_shop_assignments'
        ]
        
        for migration in migrations_to_remove:
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'tracker' AND name = %s
            """, [migration])
            print(f"✅ Removed {migration} from migration history")
        
        # Also remove the unapplied migrations to start fresh
        unapplied_migrations = [
            '0013_4_create_shop_model',
            '0013_5_add_display_name_to_shop'
        ]
        
        for migration in unapplied_migrations:
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'tracker' AND name = %s
            """, [migration])
            print(f"✅ Removed {migration} from migration history")
    
    print("✅ Migration history fixed")

if __name__ == "__main__":
    try:
        fix_migration_history()
        print("🎉 Migration fix completed successfully")
    except Exception as e:
        print(f"❌ Migration fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
