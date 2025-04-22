# Web Research Agent

A powerful AI-powered tool that can search the web, extract relevant information, and compile comprehensive research reports based on user queries.

## Features

- Analyzes user queries to understand intent and determine search strategy
- Searches the web for relevant information
- Extracts and analyzes content from websites
- Aggregates news articles on specific topics
- Synthesizes information from multiple sources
- Generates comprehensive research reports

## Architecture

The Web Research Agent is composed of several key components:

1. **Query Analyzer:** Interprets user queries and breaks them into searchable components
2. **Search Coordinator:** Manages web searches using appropriate search terms
3. **Content Extractor:** Scrapes relevant information from web pages
4. **Information Synthesizer:** Combines information from multiple sources and generates a final report
5. **Error Handler:** Manages errors throughout the process

## Tool Integration

The agent integrates with the following tools:

1. **Web Search Tool:** Uses SerpAPI to search the web and retrieve relevant search results
2. **Web Scraper:** Extracts text and data from websites using BeautifulSoup
3. **Content Analyzer:** Analyzes content relevance using OpenAI's GPT-4
4. **News Aggregator:** Finds recent news articles on specific topics

## Technical Implementation

- **Backend:** Python with Flask
- **AI Models:** OpenAI's GPT-4
- **Web Scraping:** BeautifulSoup4
- **Search API:** SerpAPI
- **Frontend:** HTML, CSS, JavaScript

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- API keys for OpenAI and SerpAPI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/web-research-agent.git
cd web-research-agent
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
SERPAPI_KEY=your_serpapi_key
```

### Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and go to `http://localhost:5000`

3. Enter your research query and click "Research"

## Usage

1. Enter a research query in the input field
2. Click the "Research" button
3. Wait for the agent to complete its research
4. View the comprehensive research report

## Error Handling

The agent includes robust error handling for:
- API failures
- Website scraping issues
- Content analysis problems
- Invalid user queries

## Testing

Run the tests using:
```bash
python -m unittest discover tests
```

## Future Improvements

- Add support for more data sources
- Implement caching for faster responses
- Add user authentication
- Improve content extraction from complex websites
- Add support for PDF and document analysis
