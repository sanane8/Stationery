release: python manage.py migrate --settings=stationery_tracker.production_settings
web: gunicorn stationery_tracker.wsgi --bind 0.0.0.0:$PORT --access-logfile - --error-logfile -
