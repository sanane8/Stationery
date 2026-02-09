
# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
# Railway: Use stdout/stderr instead of file paths
accesslog = "-"
errorlog = "-"
loglevel = "info"
daemon = False
# Railway: Remove pidfile and user/group (not needed in container)
# pidfile = "/var/run/gunicorn/gunicorn.pid"
# user = "www-data"
# group = "www-data"
tmp_upload_dir = None
