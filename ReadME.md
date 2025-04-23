# **🔍 Web Research Agent**

A powerful web research assistant that automates online research tasks using AI.

## **🌐 Live Demo**

Try out the Web Research Agent at: [https://webresearchagent.onrender.com/](https://webresearchagent.onrender.com/)

Note: The application is deployed on Render's free tier with limited resources (0.1 CPU, 512MB RAM), so response times may vary based on query complexity.

## **✨ Features**

* **Automated Web Search:** 🌐 Search across multiple sources, hands-free!
* **Content Extraction & Analysis:** 🧠 Extracts and analyzes content for maximum relevance.
* **Information Synthesis:** 📝 Compiles findings into comprehensive reports.
* **News Aggregation:** 📰 Gathers the latest news on your chosen topics.

## **🛠️ Technical Implementation**

* **Backend:** Python with Flask 🐍
* **AI Models:** Google Gemini 1.5 Pro 🤖
* **Web Scraping:** BeautifulSoup4 🍜
* **Search API:** SerpAPI 🔍
* **Frontend:** HTML, CSS, JavaScript 🎨

## **🔗 Tool Integration**

The agent integrates with the following tools:

1. **Web Search Tool:** Uses SerpAPI to scour the web and deliver relevant search results.
2. **Web Scraper:** Employs BeautifulSoup to extract text and data from websites.
3. **Content Analyzer:** Leverages Google's Gemini model to analyze content relevance.
4. **News Aggregator:** Finds recent news articles on specific topics.

## **🚀 Setup Instructions**

### **Prerequisites**

* Python 3.x
* Git

### **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/web-research-agent.git
   cd web-research-agent
   ```

2. Create a virtual environment and activate it:
   ```bash
   # For Linux/macOS
   python -m venv venv
   source venv/bin/activate

   # For Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### **Configuration**

1. Create a .env file in the root directory of the project.
2. Add your API keys to the .env file:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   SERPAPI_KEY=your_serpapi_key
   ```

## **🎯 Usage**

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to http://localhost:8080 (or the port specified by the application).
3. Enter your research query in the input field and click "Research".

## **⚠️ Error Handling and Limitations**

### **Current Limitations**

1. **API Dependency:** The application relies on external APIs (SerpAPI and Google Gemini). Availability and usage limits of these services may affect functionality.
2. **Content Extraction:** Web scraping can be unreliable for websites with complex JavaScript rendering or anti-scraping measures.
3. **Processing Time:** Complex queries requiring extensive searching and analysis can take significant time to process.
4. **Concurrent Requests:** The current setup might have limitations on handling a large number of simultaneous requests (e.g., limited to 3 concurrent requests as mentioned).

## **📜 License**

[MIT License](LICENSE)
