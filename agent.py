import os
import json
from tools import WebSearchTool, WebScraperTool, ContentAnalyzerTool, NewsAggregatorTool
import google.generativeai as genai
import re
from dotenv import load_dotenv
import gc  # Garbage collection
import time  # For rate limiting

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class WebResearchAgent:
    def __init__(self):
        self.web_search = WebSearchTool()
        self.web_scraper = WebScraperTool()
        self.content_analyzer = ContentAnalyzerTool()
        self.news_aggregator = NewsAggregatorTool()
        self.model = genai.GenerativeModel('gemini-1.5-pro')

        # Severely reduce limits for low resource environment (0.1 CPU, 512MB RAM)
        self.max_search_terms = 1  # Reduced from 2
        self.max_results_per_term = 1  # Reduced from 2
        self.max_total_results = 2  # Reduced from 6
        self.max_extracted_sources = 1  # Reduced from 2
        self.max_synthesis_content_length = 150  # Reduced from 300

        # Add rate limiting to prevent CPU spikes
        self.last_api_call = 0
        self.min_api_interval = 2  # seconds between API calls

    def _rate_limit(self):
        """Apply rate limiting to prevent CPU spikes"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_api_interval:
            time.sleep(self.min_api_interval - time_since_last_call)
        self.last_api_call = time.time()

    def analyze_query(self, query):
        """
        Analyzes the user query to understand intent and determine search strategy
        """
        try:
            # Apply rate limiting
            self._rate_limit()

            # Simplify prompt to reduce token usage
            prompt = f"""Analyze this query: "{query}"
            Return JSON with: main_topic, key_aspects, content_type, search_terms.
            Be very concise. Limit search_terms to 1-2 terms maximum.
            """

            response = self.model.generate_content(prompt)
            response_text = response.text

            # Parse JSON from response
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
                analysis = json.loads(json_str)
                # Clear variables to free memory
                del response
                del response_text
                del json_str
                gc.collect()
                return analysis
            except json.JSONDecodeError:
                # Fallback response
                return {
                    "main_topic": query,
                    "key_aspects": [query],
                    "content_type": "facts",
                    "search_terms": [query]
                }
        except Exception as e:
            print(f"Error analyzing query: {e}")
            return {
                "main_topic": query,
                "key_aspects": [query],
                "content_type": "facts",
                "search_terms": [query]
            }
        finally:
            # Force garbage collection
            gc.collect()

    def search_web(self, search_terms, is_news=False):
        """
        Searches the web using generated search terms
        Optimized for low resource environment
        """
        results = []
        # Limit search terms using the configurable limit
        search_terms = search_terms[:self.max_search_terms]

        for term in search_terms:
            # Apply rate limiting between searches
            time.sleep(1)

            if is_news:
                term_results = self.news_aggregator.get_news(term, max_results=self.max_results_per_term)
            else:
                term_results = self.web_search.search(term, num_results=self.max_results_per_term)

            results.extend(term_results)

            # Clear variables to free memory
            del term_results
            gc.collect()

        # Simplified deduplication to save memory
        unique_results = []
        urls = set()

        for result in results:
            url = result["link"]
            if url not in urls:
                unique_results.append(result)
                urls.add(url)

                # Break if we've reached our limit
                if len(unique_results) >= self.max_total_results:
                    break

        # Clear variables to free memory
        del results
        del urls
        gc.collect()

        return unique_results

    def extract_content(self, search_results, query):
        """
        Extracts and analyzes content from search results
        Optimized for low resource environment
        """
        extracted_data = []
        # Limit to configurable max results to process
        search_results = search_results[:self.max_total_results]

        for result in search_results:
            # Apply rate limiting between scraping operations
            time.sleep(1)

            url = result["link"]
            scraped_data = self.web_scraper.scrape(url)

            if scraped_data["content"]:
                # Apply rate limiting before analysis
                time.sleep(1)

                analysis = self.content_analyzer.analyze(scraped_data["content"], query)

                if analysis.get("relevance_score", 0) >= 5:  # Only keep relevant content
                    extracted_data.append({
                        "title": scraped_data["title"],
                        "url": url,
                        "content": analysis.get("relevant_content", ""),
                        "relevance_score": analysis.get("relevance_score", 0)
                    })

                # Clear variables to free memory
                del scraped_data
                del analysis
                gc.collect()

        # Sort by relevance score
        extracted_data.sort(key=lambda x: x["relevance_score"], reverse=True)
        # Limit to configurable top most relevant results
        extracted_data = extracted_data[:self.max_extracted_sources]

        gc.collect()
        return extracted_data

    def synthesize_information(self, extracted_data, query):
        """
        Synthesizes extracted information into a comprehensive report
        Optimized for low resource environment
        """
        try:
            # Apply rate limiting
            self._rate_limit()

            # Prepare content for synthesis
            context = []
            # Limit to configurable top sources
            extracted_data = extracted_data[:self.max_extracted_sources]

            for item in extracted_data:
                # Limit content length for each source using the configurable limit
                content = item.get('content', '')
                if len(content) > self.max_synthesis_content_length:
                    content = content[:self.max_synthesis_content_length] + "..."

                context.append(f"Source: {item.get('title', 'Unknown')} ({item.get('url', '')})\n{content}\n")

            context_text = "\n".join(context)

            # Simplified prompt to reduce token usage
            prompt = f"""Based on this information, answer: "{query}"

            INFORMATION:
            {context_text}

            Create a concise report (max 500 words) that answers the query.
            Include proper citations.
            """

            response = self.model.generate_content(prompt)
            report = response.text

            # Add sources at the end
            sources = "\n\nSources:\n"
            for i, item in enumerate(extracted_data):
                sources += f"{i+1}. {item.get('title', 'Unknown')} - {item.get('url', '')}\n"

            # Clear variables to free memory
            del context
            del context_text
            del prompt
            del response
            gc.collect()

            return report + sources
        except Exception as e:
            print(f"Error synthesizing information: {e}")
            return "Failed to synthesize information due to an error."
        finally:
            # Force garbage collection
            gc.collect()

    def research(self, query):
        """
        Main method to perform web research based on user query
        Optimized for low resource environment
        """
        try:
            # Step 1: Analyze the query
            analysis = self.analyze_query(query)
            print(f"Query analysis: {analysis}")

            # Step 2: Search for general information
            # Check if search_terms exists and is a list
            if "search_terms" not in analysis or not analysis["search_terms"]:
                analysis["search_terms"] = [query]  # Use the original query as fallback
            elif not isinstance(analysis["search_terms"], list):
                analysis["search_terms"] = [analysis["search_terms"]]  # Convert to list if it's a string

            # Process search terms
            search_terms = analysis["search_terms"][:self.max_search_terms]
            search_results = self.search_web(search_terms)

            # Clear memory after each major step
            gc.collect()

            # Step 3: Extract and analyze content
            extracted_data = self.extract_content(search_results, query)

            # Clear memory after each major step
            del search_results
            gc.collect()

            # Step 4: Synthesize information
            if extracted_data:
                report = self.synthesize_information(extracted_data, query)

                # Clear variables to free memory
                del analysis
                del extracted_data
                gc.collect()

                return report
            else:
                return "I couldn't find relevant information for your query. Please try with different search terms."
        except Exception as e:
            print(f"Error in research process: {e}")
            return f"An error occurred during the research process: {str(e)}"
        finally:
            # Force garbage collection at the end
            gc.collect()
