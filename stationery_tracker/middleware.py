"""
Production middleware for graceful error handling.
"""
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.core.management import call_command
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseErrorMiddleware:
    """
    Middleware to handle database connection errors gracefully.
    On first request, ensures migrations are run.
    """
    
    _migrations_checked = False
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # On first request, check and run migrations if needed
        if not DatabaseErrorMiddleware._migrations_checked:
            self._ensure_migrations()
            DatabaseErrorMiddleware._migrations_checked = True
        
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Catch database errors and return a user-friendly response
            error_msg = str(e)
            if 'relation' in error_msg.lower() or 'table' in error_msg.lower() or 'auth_user' in error_msg:
                logger.error(f"Database schema error: {e}")
                # Trigger migrations
                try:
                    self._run_migrations()
                except Exception as migrate_err:
                    logger.error(f"Failed to run migrations: {migrate_err}")
                
                # Return a user-friendly error
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Database is initializing. Please try again in a few seconds.',
                        'status': 'maintenance'
                    }, status=503)
                else:
                    return HttpResponse(
                        '<h1>Service Initializing</h1><p>The database is being set up. Please refresh the page in a few seconds.</p>',
                        status=503,
                        content_type='text/html'
                    )
            raise
    
    def _ensure_migrations(self):
        """Check if migrations have been run; run them if not."""
        try:
            # Try a simple query to see if tables exist
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM django_migrations LIMIT 1;")
        except Exception as e:
            # Tables don't exist; run migrations
            logger.info("Django migrations table not found; running migrations...")
            self._run_migrations()
    
    def _run_migrations(self):
        """Run Django migrations."""
        try:
            # Only run in production to avoid repeated migrations
            if os.environ.get('DJANGO_SETTINGS_MODULE') == 'stationery_tracker.production_settings':
                logger.info("Running Django migrations...")
                call_command('migrate', '--noinput', verbosity=0)
                logger.info("Migrations completed successfully.")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
