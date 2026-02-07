"""
WSGI config for stationery_tracker project.
PythonAnywhere: ensure project root is on sys.path (add your path in the Web tab if needed).
"""

import os
import sys

# Add project root to path (required on PythonAnywhere and some servers)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
