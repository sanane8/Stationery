import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import Sale
from django.db.models import Count, Q

try:
    # Test the query that's causing issues
    sales = Sale.objects.select_related('customer', 'created_by').prefetch_related('items__item').annotate(
        item_count=Count('items')
    ).filter(
        Q(item_count__gt=0) | Q(notes__contains='Payment for Debt')
    ).order_by('-sale_date')
    
    print(f"Query successful! Found {sales.count()} sales")
    
    # Try to iterate through first few
    for i, sale in enumerate(sales[:5]):
        print(f"Sale #{sale.id}: {sale.notes[:50]}...")
        
except Exception as e:
    print(f"Query error: {e}")
    import traceback
    traceback.print_exc()
