# Gunicorn configuration for Railway
import os

# Bind to the port provided by Railway
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Performance settings
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
daemon = False

# Security
tmp_upload_dir = None
capture_output = False

# Disable syslog
syslog = False
syslog_prefix = None
syslog_facility = "user"
