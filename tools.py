import requests
import json
import os
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from dotenv import load_dotenv
import google.generativeai as genai
import re

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class WebSearchTool:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

    def search(self, query, num_results=5):
        """
        Performs a web search using SerpAPI and returns search results
        """
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "num": num_results
            }
            search = GoogleSearch(params)
            results = search.get_dict()

            search_results = []
            if "organic_results" in results:
                for result in results["organic_results"][:num_results]:
                    search_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", "")
                    })

            return search_results
        except Exception as e:
            print(f"Error in web search: {e}")
            return []

class WebScraperTool:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape(self, url):
        """
        Scrapes the content of a webpage and returns it as text
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # Get page text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Extract title
            title = soup.title.string if soup.title else "No title found"

            # In WebScraperTool.scrape
            return {
                "title": title,
                "content": text[:25000],  # Reduced from 50000
                "url": url
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                "title": "Error scraping page",
                "content": "",
                "url": url
            }

class ContentAnalyzerTool:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def analyze(self, text, query):
        """
        Analyzes text content for relevance to the query
        """
        try:
            # Truncate text if too long
            # In ContentAnalyzerTool.analyze
            max_length = 7500  # Reduced from 15000
            if len(text) > max_length:
                text = text[:max_length]

            prompt = f"""Analyze the following text for information relevant to this query: '{query}'.
            Return a JSON object with two fields: 'relevance_score' (0-10 scale) and 'relevant_content' (extracted relevant information).

            Text to analyze: {text}"""

            response = self.model.generate_content(prompt)

            # Process the response to extract JSON
            response_text = response.text

            # Find JSON content between code blocks if present
            json_match = re.search(r'```(?:json)?\s*(.*?)```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find anything that looks like JSON
                json_str = re.search(r'(\{.*\})', response_text, re.DOTALL)
                if json_str:
                    json_str = json_str.group(1)
                else:
                    json_str = response_text

            try:
                result = json.loads(json_str)
                # Ensure the result has the expected fields
                if "relevance_score" not in result:
                    result["relevance_score"] = 5
                if "relevant_content" not in result:
                    result["relevant_content"] = "No relevant content extracted"
                return result
            except json.JSONDecodeError:
                # If we can't parse JSON, return a default response
                return {"relevance_score": 5, "relevant_content": response_text[:1000]}

        except Exception as e:
            print(f"Error in content analysis: {e}")
            return {"relevance_score": 0, "relevant_content": ""}

class NewsAggregatorTool:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

    def get_news(self, topic, max_results=5):
        """
        Gets recent news articles on a specific topic
        """
        try:
            params = {
                "engine": "google",
                "q": topic,
                "tbm": "nws",  # News search
                "api_key": self.api_key,
                "num": max_results
            }
            search = GoogleSearch(params)
            results = search.get_dict()

            news_results = []
            if "news_results" in results:
                for result in results["news_results"][:max_results]:
                    news_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", ""),
                        "date": result.get("date", "")
                    })

            return news_results
        except Exception as e:
            print(f"Error in news aggregation: {e}")
            return []
