web: gunicorn stationery_tracker.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --max-requests 100 --keep-alive 2 --preload --access-logfile - --error-logfile - --log-level warning
