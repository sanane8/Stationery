release: DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings python manage.py migrate
web: DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings gunicorn stationery_tracker.wsgi --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile - --log-level info
