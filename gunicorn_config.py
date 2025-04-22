# Server socket
bind = "0.0.0.0:8000"

# Worker processes - absolute minimum for 512MB RAM
workers = 1
worker_class = "sync"
worker_connections = 500  # Reduced from 1000

# Timeout settings - increased to handle complex queries
timeout = 600  # 10 minutes (increased from 5)
graceful_timeout = 30  # Increased from 20
keepalive = 2

# Memory management - aggressive recycling for low memory
max_requests = 3  # Recycle workers even more frequently
max_requests_jitter = 2  # Small jitter to prevent all workers recycling at once

# Logging - minimal logging to save memory
accesslog = "-"
errorlog = "-"
loglevel = "warning"  # Only log warnings and errors

# Process naming
proc_name = "web_research_agent"

# Limit worker memory usage - stricter limits
limit_request_line = 2048
limit_request_fields = 50
limit_request_field_size = 4096

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

# Add worker timeout handler
def worker_abort(worker):
    import gc
    gc.collect()

# Add memory monitoring
def on_starting(server):
    import psutil
    print(f"Available memory: {psutil.virtual_memory().available / (1024 * 1024):.2f} MB")
