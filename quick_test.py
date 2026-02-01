import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from tracker.views import sales_list

# Create a mock request
factory = RequestFactory()
request = factory.get('/sales/')

# Get the first user and set as request user
user = User.objects.first()
if user:
    request.user = user
    
    try:
        response = sales_list(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Sales view works correctly!")
        else:
            print(f"❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error in sales view: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No user found in database")
