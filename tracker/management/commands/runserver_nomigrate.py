import os
import shutil
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = 'Start server with fresh database to avoid migration errors'

    def handle(self, *args, **options):
        # Remove the problematic database file
        db_path = settings.BASE_DIR / 'db.sqlite3'
        if db_path.exists():
            self.stdout.write(f'Removing problematic database: {db_path}')
            os.remove(db_path)
        
        # Create fresh database without migrations
        port = os.environ.get('PORT', '8000')
        self.stdout.write(f'Starting fresh server on port {port}...')
        call_command('runserver', f'0.0.0.0:{port}')
