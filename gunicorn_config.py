import os
from dotenv import load_dotenv

load_dotenv()

# Server socket
bind = "0.0.0.0:8080"
backlog = 64

# Worker processes
workers = 2  # Reduce number of workers
worker_class = 'sync'
worker_connections = 100
timeout = int(os.getenv('WORKER_TIMEOUT', 300))  # Increase timeout
max_requests = int(os.getenv('WORKER_MAX_REQUESTS', 10))
max_requests_jitter = 3

# Process naming
proc_name = 'web_research_agent'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process management
preload_app = True

# Memory management
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
