#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.forms import SaleItemForm

def test_sale_item_form():
    print("Testing SaleItemForm...")
    
    # Test form instantiation
    try:
        form = SaleItemForm()
        print("✓ SaleItemForm instantiated successfully")
        
        # Check default quantity value
        default_quantity = form.fields['quantity'].initial
        print(f"Default quantity: {default_quantity}")
        
        if default_quantity == 1:
            print("✓ Default quantity is correctly set to 1")
        else:
            print("✗ Default quantity is not 1")
        
        # Check field attributes
        quantity_widget = form.fields['quantity'].widget
        print(f"Quantity widget attributes: {quantity_widget.attrs}")
        
        if 'min' in quantity_widget.attrs and quantity_widget.attrs['min'] == '1':
            print("✓ Quantity field has min=1 attribute")
        else:
            print("✗ Quantity field missing min=1 attribute")
            
    except Exception as e:
        print(f"✗ Error creating form: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_sale_item_form()
