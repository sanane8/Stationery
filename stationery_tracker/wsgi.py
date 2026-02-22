"""
WSGI config for stationery_tracker project.
"""

import os
import sys

# Add project root to path (required on some servers)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')

from django.core.wsgi import get_wsgi_application

# Auto-run migrations on first startup (idempotent - safe to run multiple times)
def run_startup_migrations():
    """Run migrations once on app startup."""
    try:
        import django
        django.setup()
        from django.core.management import call_command
        from django.db import connection
        
        # Check if migrations table exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM django_migrations LIMIT 1;")
        except Exception:
            # Migrations table doesn't exist; run migrations
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Running Django migrations on startup...")
            call_command('migrate', '--noinput', verbosity=0)
            logger.info("Migrations completed.")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during startup migrations: {e}")
        # Don't crash startup if migrations fail

# Run migrations on startup (only once per process)
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'stationery_tracker.production_settings':
    run_startup_migrations()

application = get_wsgi_application()
