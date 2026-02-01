import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.db import connection
from django.utils import timezone
from datetime import timedelta

# Calculate yesterday's date
yesterday = timezone.now().date() - timedelta(days=1)
yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
yesterday_end = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.max.time()))

print(f'Looking for sales deleted yesterday: {yesterday}')
print(f'Time range: {yesterday_start} to {yesterday_end}')
print()

# Check Django admin log for sales deleted yesterday
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT 
            object_id,
            object_repr,
            action_time,
            user_id,
            change_message
        FROM django_admin_log 
        WHERE content_type_id IN (
            SELECT id FROM django_content_type WHERE model = 'sale'
        ) 
        AND action_flag = 3
        AND action_time >= %s
        AND action_time <= %s
        ORDER BY action_time DESC
    """, [yesterday_start, yesterday_end])
    
    deleted_sales = cursor.fetchall()
    
    if deleted_sales:
        print(f'Found {len(deleted_sales)} sales deleted yesterday:')
        print()
        
        # Get user information
        user_ids = list(set([sale[3] for sale in deleted_sales if sale[3]]))
        users = {}
        if user_ids:
            cursor.execute(f"SELECT id, username FROM auth_user WHERE id IN ({','.join(map(str, user_ids))})")
            users = dict(cursor.fetchall())
        
        for i, sale in enumerate(deleted_sales, 1):
            sale_id = sale[0]
            sale_repr = sale[1]
            action_time = sale[2]
            user_id = sale[3]
            change_message = sale[4]
            
            username = users.get(user_id, 'Unknown') if user_id else 'Unknown'
            
            print(f'{i}. Sale ID: {sale_id}')
            print(f'   Details: {sale_repr}')
            print(f'   Deleted at: {action_time}')
            print(f'   Deleted by: {username}')
            print(f'   Change message: {change_message}')
            print()
    else:
        print('No sales were deleted yesterday.')
        
        # Let's also check for any sales deleted in the last few days for context
        print()
        print('Recent deleted sales (last 7 days):')
        
        week_ago = timezone.now() - timedelta(days=7)
        cursor.execute("""
            SELECT 
                object_id,
                object_repr,
                action_time,
                user_id
            FROM django_admin_log 
            WHERE content_type_id IN (
                SELECT id FROM django_content_type WHERE model = 'sale'
            ) 
            AND action_flag = 3
            AND action_time >= %s
            ORDER BY action_time DESC
            LIMIT 10
        """, [week_ago])
        
        recent_deleted = cursor.fetchall()
        if recent_deleted:
            for sale in recent_deleted:
                print(f'  - {sale[1]} at {sale[2]}')
        else:
            print('  No recent deleted sales found.')

print()
print('Note: This information comes from the Django admin log.')
print('The actual sales data is permanently deleted from the main database tables.')
print('To recover the actual sales data, you would need:')
print('1. Database backups from before the deletion')
print('2. Or implement data restoration from the admin log information')
