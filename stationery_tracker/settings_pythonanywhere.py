"""
Django settings for PythonAnywhere deployment
This removes Heroku-specific configurations
"""

from .settings import *

# Remove Heroku configuration
# django_heroku.settings(locals())  # This line causes the error

# PythonAnywhere specific settings
import os

# Database - use SQLite for PythonAnywhere free tier
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Override environment variables for PythonAnywhere
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production-key-12345')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Allowed hosts for PythonAnywhere
username = os.getenv('PYTHONANYWHERE_USERNAME', 'yourusername')
ALLOWED_HOSTS = [
    f'{username}.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Static files configuration for PythonAnywhere
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Session settings
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend for PythonAnywhere (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging configuration for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
