#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import ProductCategory, Shop

shop = Shop.objects.get(name='duka_la_vinywaji')

# Simulate what the form does
categories = ProductCategory.objects.all()
categories_filtered = categories.filter(shop=shop)

print(f"Total ProductCategories: {ProductCategory.objects.count()}")
print(f"ProductCategories for shop '{shop.display_name}': {categories_filtered.count()}")
print("\nCategories in dropdown:")
for cat in categories_filtered.order_by('name'):
    print(f"  - {cat.name}")

# Check if MAJI is included
maji_exists = categories_filtered.filter(name='MAJI').exists()
print(f"\n'MAJI' exists in filtered list: {maji_exists}")
