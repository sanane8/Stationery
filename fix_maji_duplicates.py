#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import ProductCategory, Shop

shop = Shop.objects.get(name='duka_la_vinywaji')

# Find all Maji entries (case-insensitive)
maji_entries = ProductCategory.objects.filter(shop=shop, name__iexact='Maji')
print(f"Found {maji_entries.count()} MAJI entries:")
for entry in maji_entries:
    print(f"  ID: {entry.id}, Name: '{entry.name}'")

# If there are duplicates, keep only one
if maji_entries.count() > 1:
    print("\nRemoving duplicates...")
    to_delete = maji_entries[1:]  # Keep first, delete others
    for entry in to_delete:
        print(f"  Deleting ID {entry.id} ('{entry.name}')")
        entry.delete()

# Verify final state
final_cats = ProductCategory.objects.filter(shop=shop, name__iexact='Maji')
print(f"\nFinal count: {final_cats.count()}")

# Show all categories
print("\nAll ProductCategories for Duka la Vinywaji:")
all_cats = ProductCategory.objects.filter(shop=shop).order_by('name')
for cat in all_cats:
    print(f"  - {cat.name}")
