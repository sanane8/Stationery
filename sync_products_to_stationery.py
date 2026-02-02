#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import Product, StationeryItem, Category

def sync_products_to_stationery():
    """Create stationery items for existing products and sync stock"""
    
    print("🔄 Syncing Products to Stationery Items...")
    print("=" * 50)
    
    products = Product.objects.all()
    print(f"Found {products.count()} products to sync")
    
    for product in products:
        print(f"\n📦 Processing: {product.name} ({product.sku})")
        
        # Create stationery item if not exists
        if not product.stationery_item:
            print("  ➕ Creating stationery item...")
            product.create_stationery_item()
            print(f"  ✅ Created stationery item: {product.stationery_item.name}")
        else:
            print("  📋 Stationery item already exists")
        
        # Sync stock
        print(f"  🔄 Syncing stock...")
        product.sync_with_stationery_item()
        
        # Display sync status
        if product.stationery_item:
            print(f"  📊 Stock Status:")
            print(f"     Product: {product.cartons_in_stock} cartons × {product.units_per_carton} units = {product.total_units_in_stock} units")
            print(f"     Stationery: {product.stationery_item.stock_quantity} units")
            print(f"     ✅ Sync Status: {'✅ MATCH' if product.total_units_in_stock == product.stationery_item.stock_quantity else '❌ MISMATCH'}")
        else:
            print(f"     ❌ No stationery item linked")
    
    print("\n" + "=" * 50)
    print("🎉 Sync Complete!")
    
    # Summary
    total_products = Product.objects.count()
    linked_products = Product.objects.filter(stationery_item__isnull=False).count()
    
    print(f"\n📈 Summary:")
    print(f"   Total Products: {total_products}")
    print(f"   Linked to Stationery: {linked_products}")
    print(f"   Not Linked: {total_products - linked_products}")
    
    # Verify all stationery items
    print(f"\n🔍 Verification:")
    stationery_items = StationeryItem.objects.all()
    print(f"   Total Stationery Items: {stationery_items.count()}")
    
    for item in stationery_items:
        if hasattr(item, 'product'):
            print(f"   📦 {item.name}: {item.stock_quantity} units (linked to product)")
        else:
            print(f"   📦 {item.name}: {item.stock_quantity} units (standalone)")

if __name__ == "__main__":
    sync_products_to_stationery()
