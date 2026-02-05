import os
import sys
from pathlib import Path

# Add your project directory to Python path
project_home = '/home/yourusername/stationery_pythonanywhere'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings_pythonanywhere')

# Configure Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
