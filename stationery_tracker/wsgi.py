"""
WSGI config for stationery_tracker project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')

application = get_wsgi_application()
