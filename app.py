from flask import Flask, request, render_template, jsonify
from agent import WebResearchAgent
import gc

app = Flask(__name__)
research_agent = WebResearchAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/research', methods=['POST'])
def perform_research():
    query = request.json.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        result = research_agent.research(query)
        # Force garbage collection after processing
        gc.collect()
        return jsonify({'result': result})
    except Exception as e:
        # Force garbage collection on error
        gc.collect()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
