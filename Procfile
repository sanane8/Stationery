release: python manage.py migrate
web: gunicorn stationery_tracker.wsgi --bind 0.0.0.0:$PORT
