from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Start server without running migrations'

    def handle(self, *args, **options):
        # Skip migrations and start server directly
        port = os.environ.get('PORT', '8000')
        self.stdout.write(f'Starting server on port {port} without migrations...')
        call_command('runserver', f'0.0.0.0:{port}')
