#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from tracker.forms import DebtForm
from tracker.models import Customer, StationeryItem

def test_debt_form():
    print("Testing DebtForm...")
    
    # Test form instantiation
    try:
        form = DebtForm()
        print("✓ DebtForm instantiated successfully")
        
        # Check if all required fields are present
        expected_fields = ['customer', 'sale', 'item', 'quantity', 'amount', 'due_date', 'description']
        actual_fields = list(form.fields.keys())
        
        print(f"Expected fields: {expected_fields}")
        print(f"Actual fields: {actual_fields}")
        
        missing_fields = set(expected_fields) - set(actual_fields)
        if missing_fields:
            print(f"✗ Missing fields: {missing_fields}")
        else:
            print("✓ All required fields present")
        
        # Check unit_prices
        if hasattr(form, 'unit_prices'):
            print("✓ unit_prices attribute exists")
            print(f"Unit prices data: {form.unit_prices}")
        else:
            print("✗ unit_prices attribute missing")
            
    except Exception as e:
        print(f"✗ Error creating form: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_debt_form()
