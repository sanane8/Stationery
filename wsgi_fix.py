import os
import sys

# Add project directory to Python path
path = '/home/spmsabila/Stationery'
if path not in sys.path:
    sys.path.insert(0, path)

# Change to project directory
os.chdir(path)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
