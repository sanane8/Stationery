import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.utils import timezone
from tracker.models import Sale
from datetime import timedelta

# Calculate yesterday's date
yesterday = timezone.now().date() - timedelta(days=1)
yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
yesterday_end = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.max.time()))

print(f'Looking for sales deleted on: {yesterday}')
print(f'Time range: {yesterday_start} to {yesterday_end}')
print()

# Try to find deleted sales - this is tricky in Django since they're deleted from DB
# Let's first check current sales and see if we have any audit/log tables
print('Current sales in database:')
current_sales = Sale.objects.all()
print(f'Total current sales: {current_sales.count()}')

# Check if there are any sales from yesterday that still exist
yesterday_sales = Sale.objects.filter(sale_date__date=yesterday)
print(f'Sales from yesterday that still exist: {yesterday_sales.count()}')

for sale in yesterday_sales:
    customer_name = sale.customer.name if sale.customer else "Walk-in"
    print(f'  - Sale #{sale.id}: {customer_name} - TZS {sale.total_amount}')

print()
print('Note: Once sales are deleted from the database, they cannot be retrieved')
print('unless you have database backups, audit logs, or soft-delete functionality enabled.')
print()
print('Options to recover deleted sales:')
print('1. Check database backups')
print('2. Check if there are any audit/log tables')
print('3. Check application logs')
print('4. Implement soft-delete functionality for future')
