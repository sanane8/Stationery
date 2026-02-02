#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import Sale, SaleItem, StationeryItem
from decimal import Decimal

print("🔄 Restoring Sale Item Data")
print("=" * 60)

# Get all sales with their items
sales = Sale.objects.prefetch_related('items').all()
print(f"Found {sales.count()} sales")

restored_count = 0

for sale in sales:
    print(f"\n Processing Sale #{sale.id}:")
    print(f"  Customer: {sale.customer or 'Walk-in'}")
    print(f"  Total: TZS {sale.total_amount}")
    print(f"  Items: {sale.items.count()}")
    
    for sale_item in sale.items.all():
        if not sale_item.retail_item and not sale_item.wholesale_item:
            # Try to find a matching stationery item
            stationery_items = StationeryItem.objects.filter(
                unit_price=sale_item.unit_price
            )
            
            if stationery_items.exists():
                # Use the first matching stationery item
                matching_item = stationery_items.first()
                
                # Check if this combination already exists
                existing = SaleItem.objects.filter(
                    sale=sale,
                    product_type='retail',
                    retail_item=matching_item
                ).exists()
                
                if not existing:
                    sale_item.product_type = 'retail'
                    sale_item.retail_item = matching_item
                    sale_item.save()
                    
                    restored_count += 1
                    print(f"  Restored: {matching_item.name} (TZS {sale_item.unit_price}) x {sale_item.quantity}")
                else:
                    print(f"  Duplicate found for {matching_item.name}, skipping")
            else:
                print(f"  Could not find matching stationery item for price TZS {sale_item.unit_price}")

print(f"\n Restored {restored_count} sale items!")
print("=" * 60)
