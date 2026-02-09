
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
# Use stdout/stderr for all environments to prevent file permission issues
accesslog = "-"
errorlog = "-"
loglevel = "info"
daemon = False
# Remove pidfile and user/group (not needed in container)
# pidfile = "/var/run/gunicorn/gunicorn.pid"
# user = "www-data"
# group = "www-data"
tmp_upload_dir = None
# Ensure logging goes to stdout/stderr even if systemd overrides
capture_output = False
# Explicitly disable any file-based logging
syslog = False
syslog_prefix = None
syslog_facility = "user"
