import multiprocessing

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Timeout settings
timeout = 120  # Increase timeout to 120 seconds
graceful_timeout = 30
keepalive = 2

# Memory management
max_requests = 100
max_requests_jitter = 10

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
