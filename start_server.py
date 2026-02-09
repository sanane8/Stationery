#!/usr/bin/env python
"""
Development server starter - uses Django's built-in server for Windows compatibility
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
    django.setup()
    
    # Use Django's development server for Windows
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
