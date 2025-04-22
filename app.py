from flask import Flask, request, render_template, jsonify
from agent import WebResearchAgent
import gc
import os
import threading
import queue
import psutil  # Already in your requirements.txt

app = Flask(__name__)
# Track active workers
active_workers = 0
max_workers = 3  # Maximum concurrent workers

# Create a global agent instance that can be reused
research_agent = None

@app.route('/')
def index():
    return render_template('index.html')

def process_request(query, result_queue):
    """Worker function to process research requests"""
    global active_workers, research_agent
    try:
        # Create the agent if it doesn't exist
        if research_agent is None:
            research_agent = WebResearchAgent()

        # Check memory usage before processing
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / (1024 * 1024)
        max_memory_mb = int(os.getenv('WORKER_MAX_MEMORY_MB', 256))

        if memory_usage_mb > max_memory_mb * 0.8:  # If using more than 80% of allowed memory
            gc.collect()  # Force garbage collection

        # Continue with normal processing
        agent = WebResearchAgent()
        result = agent.research(query)
        result_queue.put({"success": True, "result": result})
    except Exception as e:
        result_queue.put({"success": False, "error": str(e)})
    finally:
        global active_workers
        active_workers -= 1
        # Force garbage collection
        gc.collect()
        # Decrement active workers
        active_workers -= 1

@app.route('/research', methods=['POST'])
def perform_research():
    global active_workers

    query = request.json.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    # Check if we can handle more requests
    if active_workers >= max_workers:
        return jsonify({'error': 'Server is currently processing too many requests. Please try again later.'}), 429

    # Create a result queue for this request
    result_queue = queue.Queue()

    # Increment active workers
    active_workers += 1

    # Start worker thread
    worker = threading.Thread(target=process_request, args=(query, result_queue))
    worker.daemon = True
    worker.start()

    # Wait for result with timeout
    try:
        result = result_queue.get(timeout=120)  # Increase timeout from 60 to 120 seconds
        if result["success"]:
            return jsonify({'result': result["result"]})
        else:
            return jsonify({'error': result["error"]}), 500
    except queue.Empty:
        # Timeout occurred
        active_workers -= 1  # Decrement since we're abandoning this request
        return jsonify({'error': 'Request timed out. Please try again with a simpler query.'}), 504

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)  # Set debug to False in production
