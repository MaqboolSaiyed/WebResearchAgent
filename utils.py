import time
import gc
import json
import re
import psutil
import os

# Rate limiting utilities
def apply_rate_limit(last_call_time, min_interval):
    """
    Apply rate limiting to prevent API throttling

    Args:
        last_call_time (float): Timestamp of the last API call
        min_interval (float): Minimum interval between calls in seconds

    Returns:
        float: Current timestamp after rate limiting
    """
    current_time = time.time()
    time_since_last_call = current_time - last_call_time

    if time_since_last_call < min_interval:
        time.sleep(min_interval - time_since_last_call)

    return time.time()

# Memory management utilities
def check_memory_usage(max_memory_mb=900, threshold=0.85):
    """
    Check current memory usage and perform garbage collection if needed
    Optimized for Vercel environment (1026MB RAM)

    Args:
        max_memory_mb (int): Maximum allowed memory in MB (default: 900)
        threshold (float): Threshold percentage (0.0-1.0) to trigger garbage collection

    Returns:
        float: Current memory usage in MB
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_usage_mb = memory_info.rss / (1024 * 1024)

    if memory_usage_mb > max_memory_mb * threshold:
        gc.collect()  # Force garbage collection

    return memory_usage_mb

# JSON parsing utilities
def extract_json_from_text(text):
    """
    Extract JSON from text that may contain markdown code blocks or other formatting

    Args:
        text (str): Text that may contain JSON

    Returns:
        dict: Parsed JSON object or None if parsing fails
    """
    try:
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find anything that looks like JSON
            json_str = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_str:
                json_str = json_str.group(1)
            else:
                json_str = text

        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        return None

# Error handling utilities
def safe_request(func, *args, max_retries=3, **kwargs):
    """
    Execute a function with retry logic for API requests

    Args:
        func: Function to execute
        max_retries (int): Maximum number of retry attempts
        *args, **kwargs: Arguments to pass to the function

    Returns:
        The result of the function or None if all retries fail
    """
    retries = 0
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                print(f"Failed after {max_retries} attempts: {str(e)}")
                return None
            # Exponential backoff
            time.sleep(2 ** retries)

# Environment configuration
def get_env_variable(name, default=None):
    """
    Safely get environment variable with fallback to default

    Args:
        name (str): Name of the environment variable
        default: Default value if environment variable is not set

    Returns:
        Value of environment variable or default
    """
    return os.getenv(name, default)
