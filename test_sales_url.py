import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from tracker.views import sales_list

# Test with a mock request through the view
client = Client()

# Get or create a user
user = User.objects.first()
if not user:
    print("No user found, creating test user")
    user = User.objects.create_user('testuser', 'test@example.com', 'testpass')

# Login the client with a known user
client.login(username='pauls', password='password')

try:
    response = client.get('/sales/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Sales page loads successfully!")
    elif response.status_code == 302:
        print("Redirecting - probably to login")
        print(f"Redirect location: {response.get('Location', 'Unknown')}")
    elif response.status_code == 500:
        print("Server Error 500 - checking content...")
        print(response.content.decode()[:500])
    else:
        print(f"Other error: {response.status_code}")
        print(response.content.decode()[:500])
except Exception as e:
    print(f"Error accessing sales page: {e}")
    import traceback
    traceback.print_exc()
