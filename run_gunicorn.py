#!/usr/bin/env python
"""
Windows-compatible Gunicorn runner with explicit logging configuration
"""
import os
import sys
import logging

# Set explicit logging to stdout/stderr before importing gunicorn
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)

# Override any default file-based logging
os.environ['GUNICORN_ERROR_LOG'] = '-'
os.environ['GUNICORN_ACCESS_LOG'] = '-'

if __name__ == '__main__':
    from gunicorn.app.wsgiapp import run
    
    # Simulate command line args to use our config
    sys.argv = [
        'gunicorn',
        '--config', 'gunicorn.conf.py',
        '--bind', '0.0.0.0:8000',
        'stationery_tracker.wsgi:application'
    ]
    
    run()
