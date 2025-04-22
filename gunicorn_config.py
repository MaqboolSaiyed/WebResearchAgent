# Server socket
bind = "0.0.0.0:8000"

# Worker processes - absolute minimum for 512MB RAM
workers = 1
worker_class = "sync"
worker_connections = 500  # Reduced from 1000

# Timeout settings - balance between allowing research and preventing hangs
timeout = 300  # 5 minutes (reduced from 10)
graceful_timeout = 20  # Reduced from 30
keepalive = 2

# Memory management - aggressive recycling for low memory
max_requests = 5  # Recycle workers very frequently
max_requests_jitter = 2  # Small jitter to prevent all workers recycling at once

# Logging - minimal logging to save memory
accesslog = "-"
errorlog = "-"
loglevel = "warning"  # Only log warnings and errors

# Process naming
proc_name = "web_research_agent"

# Limit worker memory usage - stricter limits
limit_request_line = 2048  # Reduced from 4096
limit_request_fields = 50   # Reduced from 100
limit_request_field_size = 4096  # Reduced from 8190

# Pre-fork hooks for memory optimization
def pre_fork(server, worker):
    import gc
    gc.collect()

# Post-fork hooks for memory optimization
def post_fork(server, worker):
    import gc
    gc.collect()

# Worker exit hook for cleanup
def worker_exit(server, worker):
    import gc
    gc.collect()
