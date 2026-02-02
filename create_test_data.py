#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.models import Supplier, ProductCategory, Product

def create_test_data():
    """Create test data for products and suppliers"""
    
    # Create suppliers
    supplier1, created = Supplier.objects.get_or_create(
        name="Stationery Supplies Ltd",
        defaults={
            'contact_person': "John Smith",
            'phone': "+255 746 840 409",
            'email': "info@stationery.co.tz",
            'address': "Dar es Salaam, Tanzania"
        }
    )
    
    supplier2, created = Supplier.objects.get_or_create(
        name="PVC Products Tanzania",
        defaults={
            'contact_person': "Mary Johnson",
            'phone': "+255 754 123 456",
            'email': "sales@pvc.co.tz",
            'address': "Dar es Salaam, Tanzania"
        }
    )
    
    # Create categories
    category1, created = ProductCategory.objects.get_or_create(
        name="Files & Folders",
        defaults={'description': "Spring files, folders, and document organization"}
    )
    
    category2, created = ProductCategory.objects.get_or_create(
        name="PVC Products",
        defaults={'description': "PVC stationery and office supplies"}
    )
    
    # Create products
    product1, created = Product.objects.get_or_create(
        sku="PVC-SPRING-001",
        defaults={
            'name': "Spring Files PVC - Large",
            'description': "High-quality PVC spring files for document organization",
            'category': category1,
            'supplier': supplier1,
            'supplier_price': 15000.00,
            'selling_price': 20000.00,
            'units_per_carton': 100,
            'carton_weight': 5.5,
            'unit_type': 'carton',
            'cartons_in_stock': 25,
            'minimum_cartons': 10,
            'notes': "Popular item for offices and schools"
        }
    )
    
    product2, created = Product.objects.get_or_create(
        sku="PVC-SPRING-002",
        defaults={
            'name': "Spring Files PVC - Small",
            'description': "Compact PVC spring files for personal use",
            'category': category1,
            'supplier': supplier2,
            'supplier_price': 12000.00,
            'selling_price': 16000.00,
            'units_per_carton': 150,
            'carton_weight': 4.2,
            'unit_type': 'carton',
            'cartons_in_stock': 15,
            'minimum_cartons': 8,
            'notes': "Great for students and small offices"
        }
    )
    
    product3, created = Product.objects.get_or_create(
        sku="PVC-FOLDER-001",
        defaults={
            'name': "PVC Document Folders",
            'description': "Durable PVC folders for document storage",
            'category': category2,
            'supplier': supplier1,
            'supplier_price': 8000.00,
            'selling_price': 12000.00,
            'units_per_carton': 200,
            'carton_weight': 6.0,
            'unit_type': 'carton',
            'cartons_in_stock': 30,
            'minimum_cartons': 12,
            'notes': "Assorted colors available"
        }
    )
    
    print("✅ Test data created successfully!")
    print(f"Created {Supplier.objects.count()} suppliers")
    print(f"Created {ProductCategory.objects.count()} categories")
    print(f"Created {Product.objects.count()} products")
    
    # Display created products
    print("\n📦 Products created:")
    for product in Product.objects.all():
        print(f"  - {product.name} ({product.sku})")
        print(f"    Supplier: {product.supplier.name}")
        print(f"    Price: TZS {product.selling_price} per carton")
        print(f"    Stock: {product.cartons_in_stock} cartons")
        print(f"    Total Value: TZS {product.get_total_value()}")
        print()

if __name__ == "__main__":
    create_test_data()
