# Railway Database Configuration Guide

# 1. Update your settings.py DATABASES configuration to use Railway's PostgreSQL

import os

# Add this to your settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://'),
        'USER': os.environ.get('PGUSER', ''),
        'PASSWORD': os.environ.get('PGPASSWORD', ''),
        'HOST': os.environ.get('PGHOST', ''),
        'PORT': os.environ.get('PGPORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Alternative simpler approach (recommended for Railway):
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# 2. Add required packages to requirements.txt:
# dj-database-url==2.1.0
# psycopg2-binary==2.9.7

# 3. Railway deployment steps:
# - Push your code to Railway
# - Set DATABASE_URL environment variable in Railway dashboard
# - Run migrations: python manage.py migrate
# - Create superuser: python manage.py createsuperuser

# 4. For existing SQLite data, you can export and import:
# python manage.py dumpdata > data.json
# (After deploying to Railway)
# python manage.py loaddata data.json
