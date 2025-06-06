import requests
import json
import os
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from dotenv import load_dotenv
import google.generativeai as genai
import re
import gc  # Import garbage collection
import time  # For rate limiting

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class WebSearchTool:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.last_request_time = 0
        self.min_request_interval = 1  # Minimum 1 second between requests

    def search(self, query, num_results=3):
        """
        Performs a web search using SerpAPI and returns search results
        Enhanced with rate limiting and strict result limiting
        """
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last_request)

            self.last_request_time = time.time()

            # Clean and sanitize the query to handle special characters
            # This ensures question marks, exclamation marks, etc. are properly handled
            sanitized_query = query.strip()

            # Log the query for debugging
            print(f"Searching for: '{sanitized_query}'")

            # Improve search parameters for complex or simple queries
            params = {
                "engine": "google",
                "q": sanitized_query,
                "api_key": self.api_key,
                "num": num_results,
                "gl": "us",  # Search in US
                "hl": "en",  # Language English
                "safe": "active"  # Safe search
            }

            # For very short queries, try to get more diverse results
            if len(query.split()) < 3:
                params["tbs"] = "qdr:y"  # Last year results for more relevant content

            # For complex topics, focus on educational content
            if any(complex_topic in query.lower() for complex_topic in
                  ["quantum", "physics", "philosophy", "theory"]):
                params["as_sitesearch"] = ".edu"  # Focus on educational sites

            search = GoogleSearch(params)
            results = search.get_dict()

            search_results = []
            if "organic_results" in results:
                for result in results["organic_results"][:num_results]:
                    search_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "Google Search"
                    })

            # Clear variables to free memory
            del results
            gc.collect()

            # Strictly limit to exactly num_results (or fewer if not available)
            search_results = search_results[:num_results]

            return search_results
        except Exception as e:
            print(f"Error in web search: {e}")
            return []

class WebScraperTool:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.max_content_length = 2500  # Increased for Vercel's higher memory capacity

    def scrape(self, url):
        """Scrapes content from a URL with error handling and content length limits"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title and main content
            title = soup.title.string if soup.title else 'No title found'
            content = soup.get_text(separator='\n', strip=True)

            # Limit content size to prevent memory issues
            content = content[:self.max_content_length]

            return {
                "title": title,
                "content": content,
                "url": url
            }

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                "title": "Error loading page",
                "content": "",
                "url": url
            }

class ContentAnalyzerTool:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Lighter model
        # Set a reasonable content limit for low-resource environment
        self.max_analysis_length = 1000  # Balanced value between 500 and 2000
        self.last_request_time = 0
        self.min_request_interval = 1  # Minimum 1 second between requests

    def analyze(self, text, query):
        """
        Analyzes text content for relevance to the query
        Enhanced with rate limiting and chunking for long content
        """
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last_request)

            self.last_request_time = time.time()

            # Check if this is a sports-related query
            is_sports_query = any(term in query.lower() for term in
                                ["score", "match", "game", "won", "win", "ipl", "cricket", "football", "soccer", "nba", "nfl"])

            # Log the query type for debugging
            if is_sports_query:
                print(f"Analyzing content for sports query: '{query}'")
            else:
                print(f"Analyzing content for query: '{query}'")

            # Clean the query to handle special characters
            cleaned_query = query.strip()

            # Implement chunking for very long content
            if len(text) > self.max_analysis_length:
                chunks = [text[i:i+self.max_analysis_length]
                         for i in range(0, len(text), self.max_analysis_length)]
                chunks = chunks[:2]  # Limit to first 2 chunks to save resources

                all_relevant_content = []
                relevance_scores = []

                for chunk in chunks:
                    # Process each chunk with appropriate prompt based on query type
                    if is_sports_query:
                        prompt = f"""Analyze the following text for information relevant to this sports query: '{cleaned_query}'.
                        This is a SPORTS-RELATED query, so prioritize:
                        - Recent match results, scores, and outcomes
                        - Team or player performance information
                        - Latest sports news and updates
                        - Time-sensitive information (like "last night's game")

                        Return a JSON object with three fields:
                        1. 'relevance_score' (0-10 scale, score 7+ if it contains direct match results)
                        2. 'relevant_content' (extracted relevant information)
                        3. 'source_quality' (0-10 scale, indicating how authoritative the source seems)

                        Keep the relevant_content concise, maximum 800 words.

                        Text to analyze: {chunk}"""
                    else:
                        prompt = f"""Analyze the following text for information relevant to this query: '{cleaned_query}'.
                        Return a JSON object with three fields:
                        1. 'relevance_score' (0-10 scale)
                        2. 'relevant_content' (extracted relevant information)
                        3. 'source_quality' (0-10 scale, indicating how authoritative the source seems)

                        Keep the relevant_content concise, maximum 800 words.

                        Text to analyze: {chunk}"""

                    response = self.model.generate_content(prompt)

                    # Process the response to extract JSON
                    response_text = response.text

                    # Clear variables to free memory
                    del response
                    del prompt
                    gc.collect()

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
                        if "source_quality" not in result:
                            result["source_quality"] = 5

                        # Limit the size of relevant_content
                        if len(result["relevant_content"]) > 2000:
                            result["relevant_content"] = result["relevant_content"][:2000]

                        # Clear variables to free memory
                        del json_str
                        del response_text
                        gc.collect()

                        # Add result to our collections
                        relevance_scores.append(result.get("relevance_score", 5))
                        all_relevant_content.append(result.get("relevant_content", ""))

                        # Continue to next chunk instead of returning immediately
                        continue
                    except json.JSONDecodeError:
                        # If we can't parse JSON, return a default response
                        content = response_text[:800]

                        # Clear variables to free memory
                        del response_text
                        gc.collect()

                        # Add default result to our collections
                        relevance_scores.append(5)
                        all_relevant_content.append(content)

                        # Continue to next chunk instead of returning immediately
                        continue

                # After processing all chunks, combine results
                # Use the highest relevance score
                avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 5
                combined_content = " ".join(all_relevant_content)

                # Limit combined content length
                if len(combined_content) > 2000:
                    combined_content = combined_content[:2000]

                return {
                    "relevance_score": avg_relevance,
                    "relevant_content": combined_content,
                    "source_quality": 5
                }

            # For content that doesn't need chunking, process normally
            # Use different prompts for sports queries vs. regular queries
            if is_sports_query:
                prompt = f"""Analyze the following text for information relevant to this sports query: '{cleaned_query}'.
                This is a SPORTS-RELATED query, so prioritize:
                - Recent match results, scores, and outcomes
                - Team or player performance information
                - Latest sports news and updates
                - Time-sensitive information (like "last night's game")

                Return a JSON object with three fields:
                1. 'relevance_score' (0-10 scale, score 7+ if it contains direct match results)
                2. 'relevant_content' (extracted relevant information)
                3. 'source_quality' (0-10 scale, indicating how authoritative the source seems)

                Keep the relevant_content concise, maximum 800 words.

                Text to analyze: {text}"""
            else:
                prompt = f"""Analyze the following text for information relevant to this query: '{cleaned_query}'.
                Return a JSON object with three fields:
                1. 'relevance_score' (0-10 scale)
                2. 'relevant_content' (extracted relevant information)
                3. 'source_quality' (0-10 scale, indicating how authoritative the source seems)

                Keep the relevant_content concise, maximum 800 words.

                Text to analyze: {text}"""

            response = self.model.generate_content(prompt)
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
                if "source_quality" not in result:
                    result["source_quality"] = 5

                # Limit the size of relevant_content
                if len(result["relevant_content"]) > 2000:
                    result["relevant_content"] = result["relevant_content"][:2000]

                # Clear variables to free memory
                del json_str
                del response_text
                del response
                del prompt
                gc.collect()

                return result
            except json.JSONDecodeError:
                # If we can't parse JSON, return a default response
                content = response_text[:800]

                # Clear variables to free memory
                del response_text
                del response
                del prompt
                gc.collect()

                return {"relevance_score": 5, "relevant_content": content, "source_quality": 5}

        except Exception as e:
            print(f"Error in content analysis: {e}")
            return {"relevance_score": 0, "relevant_content": "", "source_quality": 0}

class NewsAggregatorTool:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.last_request_time = 0
        self.min_request_interval = 1  # Minimum 1 second between requests

    def get_news(self, topic, max_results=3):  # Reduced from 5
        """
        Gets recent news articles on a specific topic
        """
        try:
            # Clean and sanitize the topic to handle special characters
            sanitized_topic = topic.strip()

            # Log the topic for debugging
            print(f"Searching news for: '{sanitized_topic}'")

            params = {
                "engine": "google",
                "q": sanitized_topic,
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

            # Clear variables to free memory
            del results
            gc.collect()

            return news_results
        except Exception as e:
            print(f"Error in news aggregation: {e}")
            return []
