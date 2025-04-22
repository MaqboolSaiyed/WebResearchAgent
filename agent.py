import os
import json
from tools import WebSearchTool, WebScraperTool, ContentAnalyzerTool, NewsAggregatorTool
import google.generativeai as genai
import re
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class WebResearchAgent:
    def __init__(self):
        self.web_search = WebSearchTool()
        self.web_scraper = WebScraperTool()
        self.content_analyzer = ContentAnalyzerTool()
        self.news_aggregator = NewsAggregatorTool()
        self.model = genai.GenerativeModel('gemini-2.0-flash')

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

    def search_web(self, search_terms, is_news=False):
        """
        Searches the web using generated search terms
        """
        results = []
        for term in search_terms:
            if is_news:
                results.extend(self.news_aggregator.get_news(term))
            else:
                results.extend(self.web_search.search(term))

        # Remove duplicates based on URL
        unique_results = []
        urls = set()
        for result in results:
            if result["link"] not in urls:
                unique_results.append(result)
                urls.add(result["link"])

        return unique_results

    def extract_content(self, search_results, query):
        """
        Extracts and analyzes content from search results
        """
        extracted_data = []

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

        # Sort by relevance score
        extracted_data.sort(key=lambda x: x["relevance_score"], reverse=True)
        return extracted_data

    def synthesize_information(self, extracted_data, query):
        """
        Synthesizes extracted information into a comprehensive report
        """
        try:
            # Prepare content for synthesis
            context = []
            for item in extracted_data:
                context.append(f"Source: {item['title']} ({item['url']})\n{item['content']}\n")

            context_text = "\n".join(context)

            prompt = f"""Based on the following extracted information, provide a comprehensive research report answering the query: "{query}"

            EXTRACTED INFORMATION:
            {context_text}

            Create a well-structured report that:
            1. Directly answers the query
            2. Synthesizes information from multiple sources
            3. Identifies any conflicting information
            4. Includes proper citations to sources
            """

            response = self.model.generate_content(prompt)
            report = response.text

            # Add sources at the end
            sources = "\n\nSources:\n"
            for i, item in enumerate(extracted_data):
                sources += f"{i+1}. {item['title']} - {item['url']}\n"

            return report + sources
        except Exception as e:
            print(f"Error synthesizing information: {e}")
            return "Failed to synthesize information due to an error."

    def research(self, query):
        """
        Main method to perform web research based on user query
        """
        try:
            # Step 1: Analyze the query
            analysis = self.analyze_query(query)
            print(f"Query analysis: {analysis}")

            # Step 2: Search for general information
            search_results = self.search_web(analysis["search_terms"])

            # Step 3: Search for news if needed
            if analysis["content_type"] == "news" or "news" in analysis["content_type"]:
                news_results = self.search_web(analysis["search_terms"], is_news=True)
                search_results.extend(news_results)

            # Step 4: Extract and analyze content
            extracted_data = self.extract_content(search_results, query)

            # Step 5: Synthesize information
            if extracted_data:
                report = self.synthesize_information(extracted_data, query)
                return report
            else:
                return "I couldn't find relevant information for your query. Please try with different search terms."
        except Exception as e:
            print(f"Error in research process: {e}")
            return f"An error occurred during the research process: {str(e)}"
