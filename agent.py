import os
import json
from tools import WebSearchTool, WebScraperTool, ContentAnalyzerTool, NewsAggregatorTool
import google.generativeai as genai
import re
from dotenv import load_dotenv
import gc  # Garbage collection

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class WebResearchAgent:
    def __init__(self):
        self.web_search = WebSearchTool()
        self.web_scraper = WebScraperTool()
        self.content_analyzer = ContentAnalyzerTool()
        self.news_aggregator = NewsAggregatorTool()
        self.model = genai.GenerativeModel('gemini-1.5-pro')

        # Add configurable limits
        self.max_search_terms = 3
        self.max_results_per_term = 3
        self.max_total_results = 5
        self.max_extracted_sources = 3
        self.max_synthesis_content_length = 500

    def analyze_query(self, query):
        """
        Analyzes the user query to understand intent and determine search strategy
        """
        try:
            prompt = f"""Analyze this research query: "{query}"
            Break it down into:
            1. Main topic
            2. Key aspects/questions
            3. Type of content needed (facts, opinions, news, etc.)
            4. Suggested search terms
            Return your analysis as a JSON object with these fields.
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
        """
        results = []
        # Limit search terms using the configurable limit
        search_terms = search_terms[:self.max_search_terms]

        for term in search_terms:
            if is_news:
                results.extend(self.news_aggregator.get_news(term, max_results=self.max_results_per_term))
            else:
                results.extend(self.web_search.search(term, num_results=self.max_results_per_term))

        # Remove duplicates based on URL
        unique_results = []
        urls = set()
        for result in results:
            if result["link"] not in urls:
                unique_results.append(result)
                urls.add(result["link"])

                # Limit to configurable max total results
                if len(unique_results) >= self.max_total_results:
                    break

        # Force garbage collection
        gc.collect()
        return unique_results

    def extract_content(self, search_results, query):
        """
        Extracts and analyzes content from search results
        """
        extracted_data = []
        # Limit to configurable max results to process
        search_results = search_results[:self.max_total_results]

        for result in search_results:
            url = result["link"]
            scraped_data = self.web_scraper.scrape(url)

            if scraped_data["content"]:
                analysis = self.content_analyzer.analyze(scraped_data["content"], query)

                if analysis["relevance_score"] >= 5:  # Only keep relevant content
                    extracted_data.append({
                        "title": scraped_data["title"],
                        "url": url,
                        "content": analysis["relevant_content"],
                        "relevance_score": analysis["relevance_score"]
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
        """
        try:
            # Prepare content for synthesis
            context = []
            # Limit to configurable top sources
            extracted_data = extracted_data[:self.max_extracted_sources]

            for item in extracted_data:
                # Limit content length for each source using the configurable limit
                content = item['content']
                if len(content) > self.max_synthesis_content_length:
                    content = content[:self.max_synthesis_content_length] + "..."

                context.append(f"Source: {item['title']} ({item['url']})\n{content}\n")

            context_text = "\n".join(context)

            prompt = f"""Based on the following extracted information, provide a comprehensive research report answering the query: "{query}"

            EXTRACTED INFORMATION:
            {context_text}

            Create a well-structured report that:
            1. Directly answers the query
            2. Synthesizes information from multiple sources
            3. Identifies any conflicting information
            4. Includes proper citations to sources

            Keep the report concise, maximum 1000 words.
            """

            response = self.model.generate_content(prompt)
            report = response.text

            # Add sources at the end
            sources = "\n\nSources:\n"
            for i, item in enumerate(extracted_data):
                sources += f"{i+1}. {item['title']} - {item['url']}\n"

            # Clear variables to free memory
            del context
            del context_text
            del prompt
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

            # Limit the number of search terms to process
            search_terms = analysis["search_terms"][:2]  # Process max 2 search terms
            search_results = self.search_web(search_terms)

            # Step 3: Search for news if needed
            if "content_type" in analysis and (analysis["content_type"] == "news" or "news" in analysis["content_type"]):
                news_results = self.search_web(search_terms, is_news=True)
                search_results.extend(news_results[:1])  # Limit news results

            # Step 4: Extract and analyze content
            extracted_data = self.extract_content(search_results, query)

            # Step 5: Synthesize information
            if extracted_data:
                report = self.synthesize_information(extracted_data, query)

                # Clear variables to free memory
                del analysis
                del search_results
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
