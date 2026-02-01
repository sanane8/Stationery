import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.test import RequestFactory
from tracker.views import sales_list
from django.contrib.auth.models import User

# Create a mock request
factory = RequestFactory()
request = factory.get('/sales/')

# Create a user and authenticate
user = User.objects.first()
if user:
    request.user = user
    
    try:
        response = sales_list(request)
        print(f"Status Code: {response.status_code}")
        print("Sales view works correctly!")
    except Exception as e:
        print(f"Error in sales view: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No user found in database")
