"""
Django settings for stationery_tracker project.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-stationery-tracker-default-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Enable DEBUG to see full error

# Handle ALLOWED_HOSTS safely - add exact Railway domain
allowed_hosts = os.environ.get('ALLOWED_HOSTS', '*')
if allowed_hosts == '*':
    ALLOWED_HOSTS = [
        'confident-truth-production.up.railway.app',
        'stationery-production.up.railway.app',
        'localhost',
        '127.0.0.1',
        '*'
    ]
else:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(',') if host.strip()]

# Re-enable CSRF middleware with proper configuration for Django 5.1
# This is needed because templates use {% csrf_token %}

# Add CSRF trusted origins for Railway and local development
CSRF_TRUSTED_ORIGINS = [
    'https://confident-truth-production.up.railway.app',
    'https://stationery-production.up.railway.app',
    'https://*.up.railway.app',
    'https://railway.app',
    'http://confident-truth-production.up.railway.app',
    'http://stationery-production.up.railway.app',
    'http://*.up.railway.app',
    'http://railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
]

# CSRF cookie settings for development
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_ALLOW_CREDENTIALS = True
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_SAMESITE = 'Lax'

# Add CSRF debugging for development
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 3600  # 1 hour

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1800  # 30 minutes - reduced from 1 hour for security
SESSION_COOKIE_SECURE = False  # Will be True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True  # Ensure session is validated on each request
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Additional security layer

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracker',  # Our main app
    'django_humanize',
]

MIDDLEWARE = [
    'stationery_tracker.middleware.SessionSecurityMiddleware',  # Add session security middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # RE-ENABLED - needed for csrf_token
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tracker.middleware.ShopSelectionMiddleware',  # Re-enable this for shop filtering
    'tracker.middleware.UserProfileMiddleware',     # Re-enable this for user profiles
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'stationery_tracker.middleware.DatabaseErrorMiddleware',  # Keep original middleware
]

# Ensure shop middleware is always enabled for both local and Railway
# This fixes the 'filter_by_shop' attribute error
if 'tracker.middleware.ShopSelectionMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware') + 1, 'tracker.middleware.ShopSelectionMiddleware')

ROOT_URLCONF = 'stationery_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tracker.context_processors.user_role',
            ],
        },
    },
]

WSGI_APPLICATION = 'stationery_tracker.wsgi.application'

# Database
import os
import dj_database_url

# Database configuration - Railway PostgreSQL or local SQLite fallback
database_url = os.environ.get('DATABASE_URL', '').strip()
if database_url and database_url.startswith(('postgresql://', 'postgres://', 'mysql://', 'sqlite://')):
    # Railway PostgreSQL production database
    try:
        DATABASES = {
            'default': dj_database_url.parse(database_url)
        }
        # Add connection pooling for Railway (only for PostgreSQL)
        if database_url.startswith(('postgresql://', 'postgres://')):
            DATABASES['default'].update({
                'CONN_MAX_AGE': 60,
            })
    except Exception as e:
        print(f"Database URL parsing error: {e}")
        # Fallback to SQLite
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Local development SQLite database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }





# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
# Set to local timezone (Tanzania) so datetimes display correctly in templates/admin
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True
USE_L10N = True  # Add this for django_humanize compatibility

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Disable logging completely to prevent Railway crashes
LOGGING_CONFIG = None

# Memory optimization for Railway
CONN_MAX_AGE = 60
DEFAULT_AUTO_FIELD = 'BigAutoField'  # Use BigAutoField for better performance

# Ensure Django admin uses its own static files
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Email (for password reset)
# In development, reset links are printed to the console. For production, set EMAIL_BACKEND to SMTP.
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'SP Msabila Stationery <noreply@example.com>')

# Africa's Talking SMS Settings
AFRICASTALKING_USERNAME = os.getenv('AFRICASTALKING_USERNAME', 'paul.sanane@gmail.com')
AFRICASTALKING_API_KEY = os.getenv('AFRICASTALKING_API_KEY', 'atsk_70aca8c7d14163b27fc4b28bf3e6576855879ed56d7a8968ca176b64fa86364009e1aacc')
AFRICASTALKING_SENDER_ID = os.getenv('AFRICICASTALKING_SENDER_ID', 'INFO')

# Disable custom logging so WSGI never crashes
LOGGING_CONFIG = None
