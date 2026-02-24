
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-stationery-tracker-production-key-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Temporarily enabled for debugging

ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '0.0.0.0',
]
# Railway: allow specific domains
railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if railway_domain:
    ALLOWED_HOSTS.append(railway_domain)
    ALLOWED_HOSTS.append(f'.{railway_domain}')
ALLOWED_HOSTS.extend(['.railway.app', '.up.railway.app'])
ALLOWED_HOSTS.extend(['confident-truth-production.up.railway.app'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tracker.middleware.ShopSelectionMiddleware',  # Add shop middleware
    'tracker.middleware.UserProfileMiddleware',     # Add user profile middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

# Database - use DATABASE_URL on Railway (PostgreSQL), else SQLite
try:
    import dj_database_url
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgresql://'):
        config = dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
        # Add SSL settings for PostgreSQL
        config['OPTIONS'] = {
            'sslmode': 'require',
        }
        DATABASES = {
            'default': config
        }
    else:
        # Fallback to SQLite if DATABASE_URL not set or invalid
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(BASE_DIR / 'db.sqlite3'),
            }
        }
except Exception as e:
    # If dj_database_url fails, use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
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
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth URLs (required for login redirects)
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Media files (used by main urls.py)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# Disable HTTPS-only settings for environments that handle SSL externally
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Session security
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# CSRF protection for Railway domain
# The exact domain that Railway is serving on
csrf_trusted = [
    'https://stationery-production.up.railway.app',
    'http://stationery-production.up.railway.app',  # For local testing
    'https://proud-adventure-production.up.railway.app',
    'http://proud-adventure-production.up.railway.app',  # Old domain for migration
    'https://*.up.railway.app',  # Wildcard for any Railway domain
]
# Add custom domain if set
if os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
    csrf_trusted.append(f'https://{os.environ.get("RAILWAY_PUBLIC_DOMAIN")}')
    csrf_trusted.append(f'http://{os.environ.get("RAILWAY_PUBLIC_DOMAIN")}')

CSRF_TRUSTED_ORIGINS = csrf_trusted

# CSRF cookie settings - match development configuration
CSRF_COOKIE_SECURE = False  # Railway handles HTTPS at the proxy level
CSRF_COOKIE_HTTPONLY = True
CSRF_ALLOW_CREDENTIALS = True
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_SAMESITE = 'Lax'

# Email settings (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@stationery.co.tz')

# Backup settings
BACKUP_DIR = BASE_DIR / 'backups'
BACKUP_SCHEDULE = '0 2 * * *'  # Daily at 2 AM

# Detailed logging for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'tracker': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
