#!/usr/bin/env python
"""
Debug script to test Django application startup
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')

try:
    print("🔧 Testing Django setup...")
    django.setup()
    print("✅ Django setup successful")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    
    # Test models
    try:
        from tracker.models import Shop
        shop_count = Shop.objects.count()
        print(f"✅ Models loaded successfully, {shop_count} shops found")
    except Exception as e:
        print(f"⚠️  Model loading issue: {e}")
    
    # Test URL configuration
    from django.urls import reverse
    try:
        login_url = reverse('login')
        print(f"✅ URL reverse successful: {login_url}")
    except Exception as e:
        print(f"⚠️  URL reverse issue: {e}")
    
    # Test middleware
    from django.test import Client
    try:
        client = Client()
        response = client.get('/')
        print(f"✅ Root URL test: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Root URL test failed: {e}")
    
    print("🎉 All tests completed")
    
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
