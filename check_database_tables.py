import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.db import connection

# Check all tables in the database
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('All tables in database:')
    for table in tables:
        print(f'  - {table[0]}')

print()

# Check if there are any audit or log tables
audit_tables = [t[0] for t in tables if any(keyword in t[0].lower() for keyword in ['audit', 'log', 'history', 'deleted', 'archive'])]
if audit_tables:
    print('Potential audit/log tables found:')
    for table in audit_tables:
        print(f'  - {table}')
        
        # Check if this table might contain deleted sales data
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f'    Records: {count}')
                
                # Get sample columns
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f'    Columns: {[col[1] for col in columns]}')
                print()
            except Exception as e:
                print(f'    Error checking table: {e}')
                print()
else:
    print('No audit/log tables found.')

# Check Django admin log table
with connection.cursor() as cursor:
    try:
        cursor.execute("SELECT COUNT(*) FROM django_admin_log")
        log_count = cursor.fetchone()[0]
        print(f'Django admin log entries: {log_count}')
        
        if log_count > 0:
            # Check for any DELETE actions on Sale model
            cursor.execute("""
                SELECT action_flag, object_repr, action_time 
                FROM django_admin_log 
                WHERE content_type_id IN (
                    SELECT id FROM django_content_type WHERE model = 'sale'
                ) AND action_flag = 3
                ORDER BY action_time DESC
            """)
            deleted_sales = cursor.fetchall()
            
            if deleted_sales:
                print(f'Found {len(deleted_sales)} deleted sales in admin log:')
                for sale in deleted_sales:
                    print(f'  - {sale[1]} at {sale[2]}')
            else:
                print('No deleted sales found in admin log.')
                
    except Exception as e:
        print(f'Error checking admin log: {e}')
