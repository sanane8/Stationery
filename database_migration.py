#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL
For Stationery Management System - Tanzania Production
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django with production settings"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')
    django.setup()

def export_sqlite_data():
    """Export data from SQLite database"""
    print("📤 Exporting data from SQLite...")
    
    try:
        # Export all data to JSON
        execute_from_command_line(['manage.py', 'dumpdata', '--natural-foreign', '--natural-primary', '-e', 'contenttypes', '-e', 'auth.Permission', '--indent', '2', 'sqlite_data.json'])
        print("✅ Data exported to sqlite_data.json")
        return True
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return False

def import_postgresql_data():
    """Import data to PostgreSQL"""
    print("📥 Importing data to PostgreSQL...")
    
    try:
        # Import data from JSON
        execute_from_command_line(['manage.py', 'loaddata', 'sqlite_data.json'])
        print("✅ Data imported to PostgreSQL")
        return True
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        return False

def verify_migration():
    """Verify data migration was successful"""
    print("🔍 Verifying migration...")
    
    try:
        from django.contrib.auth.models import User
        from tracker.models import StationeryItem, Sale, Customer, Debt
        
        # Check counts
        user_count = User.objects.count()
        item_count = StationeryItem.objects.count()
        sale_count = Sale.objects.count()
        customer_count = Customer.objects.count()
        debt_count = Debt.objects.count()
        
        print(f"✅ Migration verification:")
        print(f"   Users: {user_count}")
        print(f"   Stationery Items: {item_count}")
        print(f"   Sales: {sale_count}")
        print(f"   Customers: {customer_count}")
        print(f"   Debts: {debt_count}")
        
        return True
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🔄 Database Migration: SQLite → PostgreSQL")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Export from SQLite
    if not export_sqlite_data():
        print("\n❌ Migration failed at export stage")
        return False
    
    # Import to PostgreSQL
    if not import_postgresql_data():
        print("\n❌ Migration failed at import stage")
        return False
    
    # Verify migration
    if not verify_migration():
        print("\n❌ Migration failed at verification stage")
        return False
    
    print("\n✅ Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the application")
    print("2. Verify all data is correct")
    print("3. Update any sequences if needed")
    print("4. Remove sqlite_data.json after verification")
    
    return True

if __name__ == "__main__":
    main()
