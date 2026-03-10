#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import StationeryItem, Shop, Debt

print('=== Targeted Cleanup of Orphaned Stationery Items ===')

# Get both shops
stationery_shop = Shop.objects.get(name='stationery')
duka_shop = Shop.objects.get(name='duka_la_vinywaji')

# Find orphaned items that should belong to Duka shop
orphaned_in_stationery = StationeryItem.objects.filter(
    product__isnull=True,
    shop=stationery_shop
)

# Keywords that suggest Duka shop items
duka_keywords = ['azam', 'energy', 'embe', 'kubwa', 'soda', 'juice', 'azam energy', 'azam cane', '7up', 'coca', 'pepsi', '7up kubwa', 'sole tape kubwa']

# Find items that should be moved to Duka shop
items_to_move = []
items_to_delete = []

for item in orphaned_in_stationery:
    name_lower = item.name.lower()
    if any(keyword in name_lower for keyword in duka_keywords):
        items_to_move.append(item)
        print(f'🔄 MOVING: {item.name} from Stationery to Duka shop')
    else:
        items_to_delete.append(item)
        print(f'🗑️ DELETING: {item.name} (orphaned stationery item)')

print(f'Items to move: {len(items_to_move)}')
print(f'Items to delete: {len(items_to_delete)}')

# Move items to Duka shop first (before any deletion)
for item in items_to_move:
    try:
        # Check if this item is referenced by any debt
        debt_references = Debt.objects.filter(item=item).exists()
        if debt_references:
            print(f'  ⚠️  Cannot move {item.name} - referenced by debt, deleting instead')
            items_to_delete.append(item)
        else:
            item.shop = duka_shop
            item.save()
            print(f'  ✅ Moved: {item.name} -> {item.shop.display_name}')
    except Exception as e:
        print(f'  ❌ Error moving {item.name}: {e}')
        items_to_delete.append(item)

# Delete items (including those that couldn't be moved)
print(f'\\nDeleting {len(items_to_delete)} items...')
for item in items_to_delete:
    try:
        item_name = item.name
        item.delete()
        print(f'  ✅ Deleted: {item_name}')
    except Exception as e:
        print(f'  ❌ Error deleting {item_name}: {e}')

print(f'\\n✅ Cleanup completed!')
print(f'Moved {len([i for i in items_to_move if i not in items_to_delete])} items to Duka shop')
print(f'Deleted {len(items_to_delete)} orphaned items')

# Verify results
remaining_stationery = StationeryItem.objects.filter(shop=stationery_shop)
remaining_duka = StationeryItem.objects.filter(shop=duka_shop)

print(f'\\nFinal counts:')
print(f'  Stationery Shop: {remaining_stationery.count()} items')
print(f'  Duka la Vinywaji: {remaining_duka.count()} items')
