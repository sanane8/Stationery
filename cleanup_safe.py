#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import StationeryItem, Shop, Debt

print('=== Safe Cleanup of Orphaned Stationery Items ===')

# Get both shops
stationery_shop = Shop.objects.get(name='stationery')
duka_shop = Shop.objects.get(name='duka_la_vinywaji')

# Find orphaned items in Stationery shop
orphaned_items = StationeryItem.objects.filter(product__isnull=True, shop=stationery_shop)
print(f'Found {orphaned_items.count()} orphaned items in Stationery shop')

# Process each orphaned item
moved_count = 0
deleted_count = 0

for item in orphaned_items:
    # Check if this item is referenced by any debt
    debt_references = Debt.objects.filter(item=item).exists()
    
    if debt_references:
        # Clear debt references first
        debts_to_clear = Debt.objects.filter(item=item)
        cleared_count = debts_to_clear.update(item=None)
        print(f'🔗 Cleared {cleared_count} debt references for {item.name}')
        
        # Now delete the item
        item.delete()
        deleted_count += 1
        print(f'🗑️ Deleted: {item.name} (was referenced by debts)')
    else:
        # Check if item should be moved to Duka shop based on naming
        name_lower = item.name.lower()
        duka_keywords = ['azam', 'energy', 'embe', 'kubwa', 'soda', 'juice', 'azam energy', 'azam cane', '7up', 'coca', 'pepsi', '7up kubwa', 'sole tape kubwa']
        
        if any(keyword in name_lower for keyword in duka_keywords):
            # Move to Duka shop
            item.shop = duka_shop
            item.save()
            moved_count += 1
            print(f'🔄 Moved: {item.name} -> {item.shop.display_name}')
        else:
            # Delete truly orphaned item
            item.delete()
            deleted_count += 1
            print(f'🗑️ Deleted: {item.name} (truly orphaned)')

print(f'\\n✅ Cleanup completed!')
print(f'Moved {moved_count} items to Duka shop')
print(f'Deleted {deleted_count} orphaned items')

# Verify results
remaining_stationery = StationeryItem.objects.filter(shop=stationery_shop)
remaining_duka = StationeryItem.objects.filter(shop=duka_shop)

print(f'\\nFinal counts:')
print(f'  Stationery Shop: {remaining_stationery.count()} items')
print(f'  Duka la Vinywaji: {remaining_duka.count()} items')
