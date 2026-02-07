"""
PythonAnywhere WSGI entry point.
Use this file path in the Web tab: .../stationery_tracker/wsgi_pythonanywhere.py
If the app fails to load, the error is written to error_wsgi.log in the project root.
"""

import os
import sys

# Project root (folder containing manage.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Write startup errors to a file so you can see them even if Error log is stale
    log_path = os.path.join(BASE_DIR, 'error_wsgi.log')
    with open(log_path, 'a') as f:
        import traceback
        f.write('\n--- %s ---\n%s\n' % (os.strftime('%Y-%m-%d %H:%M:%S'), traceback.format_exc()))
    raise
