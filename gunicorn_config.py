# Server socket
bind = "0.0.0.0:8000"

# Worker processes - use fewer workers to reduce memory usage
workers = 1  # Reduced from 2
worker_class = "sync"  # Keep sync if you don't have gevent installed
worker_connections = 1000

# Timeout settings - increase timeout for long-running research queries
timeout = 600  # 10 minutes (reduced from 15)
graceful_timeout = 30
keepalive = 2

# Memory management
max_requests = 30  # Reduced from 50
max_requests_jitter = 5  # Reduced from 10

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "web_research_agent"

# Limit worker memory usage
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
