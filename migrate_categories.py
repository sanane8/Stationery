#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import ProductCategory, Category, Product

print("🔄 Migrating Product Categories to Categories")
print("=" * 60)

# Create mapping from ProductCategory to Category
category_mapping = {
    'Files & Folders': None,
    'PVC Products': None,
}

# Find the corresponding categories in the main Category table
for pc in ProductCategory.objects.all():
    try:
        category = Category.objects.get(name=pc.name)
        category_mapping[pc.name] = category
        print(f"✅ Found mapping: {pc.name} -> Category ID {category.id}")
    except Category.DoesNotExist:
        print(f"⚠️  Category '{pc.name}' not found in main Category table")
        # Create the category if it doesn't exist
        category = Category.objects.create(
            name=pc.name,
            description=pc.description
        )
        category_mapping[pc.name] = category
        print(f"✅ Created new category: {pc.name} -> Category ID {category.id}")

print("\n📦 Updating products...")
updated_count = 0

for product in Product.objects.all():
    old_category_id = product.category_id
    pc_name = None
    
    # Find the ProductCategory name
    try:
        pc = ProductCategory.objects.get(id=old_category_id)
        pc_name = pc.name
    except ProductCategory.DoesNotExist:
        print(f"⚠️  ProductCategory with ID {old_category_id} not found")
        continue
    
    # Map to the new category
    new_category = category_mapping.get(pc_name)
    if new_category:
        product.category = new_category
        product.save()
        updated_count += 1
        print(f"✅ Updated '{product.name}': Category ID {old_category_id} -> {new_category.id}")
    else:
        print(f"❌ No mapping found for '{pc_name}'")

print(f"\n🎉 Migration complete! Updated {updated_count} products.")
print("=" * 60)
