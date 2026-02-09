#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import ProductCategory, Category, Product

print("🔍 Checking Category Data")
print("=" * 50)

print("\n📋 Product Categories:")
for pc in ProductCategory.objects.all():
    print(f"  ID {pc.id}: {pc.name}")

print("\n📋 Categories:")
for c in Category.objects.all():
    print(f"  ID {c.id}: {c.name}")

print("\n📦 Products with their current categories:")
for product in Product.objects.all():
    print(f"  {product.name} -> Category ID {product.category_id} ({product.category.name if product.category else 'None'})")

print("\n" + "=" * 50)
print("🎯 Analysis Complete!")
