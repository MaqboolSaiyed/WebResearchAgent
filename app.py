from flask import Flask, request, render_template, jsonify
from agent import WebResearchAgent

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

    result = research_agent.research(query)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
