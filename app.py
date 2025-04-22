from flask import Flask, request, render_template, jsonify
from agent import WebResearchAgent
import gc
import os
import psutil

app = Flask(__name__)
# Don't initialize the agent here
# research_agent = WebResearchAgent()

@app.before_request
def check_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024

    # If using more than 400MB (leaving buffer), abort and recycle
    if memory_mb > 400:
        import gc
        gc.collect()
        # If still over limit, return error
        if process.memory_info().rss / 1024 / 1024 > 400:
            return jsonify({'error': 'Server is under high memory pressure. Please try again later.'}), 503

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/research', methods=['POST'])
def perform_research():
    query = request.json.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        # Create a new agent instance for each request
        research_agent = WebResearchAgent()
        result = research_agent.research(query)
        # Delete the agent after use
        del research_agent
        # Force garbage collection after processing
        gc.collect()
        return jsonify({'result': result})
    except Exception as e:
        # Force garbage collection on error
        gc.collect()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)  # Set debug to False in production
