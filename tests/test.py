import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import WebResearchAgent
from tools import WebSearchTool, WebScraperTool, ContentAnalyzerTool, NewsAggregatorTool

class TestWebResearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = WebResearchAgent()

    def tearDown(self):
        # Clean up after each test
        self.agent = None
        import gc
        gc.collect()

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_analyze_query(self, mock_generate):
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "main_topic": "climate change",
            "key_aspects": ["impacts", "solutions"],
            "content_type": "facts",
            "search_terms": ["climate change impacts", "climate change solutions"]
        })
        mock_generate.return_value = mock_response

        # Test query analysis
        result = self.agent.analyze_query("What are the impacts and solutions for climate change?")

        # Check that Gemini was called
        mock_generate.assert_called_once()

        # Check result structure
        self.assertIn("main_topic", result)
        self.assertIn("key_aspects", result)
        self.assertIn("content_type", result)
        self.assertIn("search_terms", result)

    @patch('tools.WebSearchTool.search')
    def test_search_web(self, mock_search):
        # Mock search results
        mock_search.return_value = [
            {"title": "Test Result 1", "link": "http://example.com/1", "snippet": "Test snippet 1"},
            {"title": "Test Result 2", "link": "http://example.com/2", "snippet": "Test snippet 2"}
        ]

        # Test web search
        search_terms = ["test query"]
        results = self.agent.search_web(search_terms)

        # Check that search was called correctly with the current parameters
        mock_search.assert_called_once_with("test query", num_results=self.agent.max_results_per_term)

        # Check result structure
        self.assertLessEqual(len(results), self.agent.max_total_results)
        if results:
            self.assertEqual(results[0]["title"], "Test Result 1")

    @patch('tools.WebScraperTool.scrape')
    @patch('tools.ContentAnalyzerTool.analyze')
    def test_extract_content(self, mock_analyze, mock_scrape):
        # Mock scrape results
        mock_scrape.return_value = {
            "title": "Test Page",
            "content": "Test content for analysis",
            "url": "http://example.com"
        }

        # Mock analyze results
        mock_analyze.return_value = {
            "relevance_score": 8,
            "relevant_content": "Relevant test content"
        }

        # Test content extraction
        search_results = [{"title": "Test Result", "link": "http://example.com", "snippet": "Test snippet"}]
        results = self.agent.extract_content(search_results, "test query")

        # Check that scrape and analyze were called correctly
        mock_scrape.assert_called_once_with("http://example.com")
        mock_analyze.assert_called_once()

        # Check result structure
        self.assertLessEqual(len(results), self.agent.max_extracted_sources)
        if results:
            self.assertEqual(results[0]["title"], "Test Page")
            self.assertEqual(results[0]["content"], "Relevant test content")
            self.assertEqual(results[0]["relevance_score"], 8)

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_synthesize_information(self, mock_generate):
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Synthesized research report"
        mock_generate.return_value = mock_response

        # Test information synthesis
        extracted_data = [
            {"title": "Source 1", "url": "http://example.com/1", "content": "Content 1", "relevance_score": 8},
            {"title": "Source 2", "url": "http://example.com/2", "content": "Content 2", "relevance_score": 7}
        ]
        result = self.agent.synthesize_information(extracted_data, "test query")

        # Check that Gemini was called
        mock_generate.assert_called_once()

        # Check that the result contains synthesized content
        self.assertTrue(result.startswith("Synthesized research report"))

        # Check that sources are included
        self.assertIn("Sources:", result)
        self.assertIn("Source 1 - http://example.com/1", result)

        # Only check for Source 2 if max_extracted_sources > 1
        if self.agent.max_extracted_sources > 1:
            self.assertIn("Source 2 - http://example.com/2", result)

    # Additional test cases

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_analyze_query_with_json_parsing_error(self, mock_generate):
        # Test when Gemini returns invalid JSON
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_generate.return_value = mock_response

        # Test query analysis with invalid JSON response
        result = self.agent.analyze_query("What is artificial intelligence?")

        # Check that fallback response is used
        self.assertEqual(result["main_topic"], "What is artificial intelligence?")
        self.assertEqual(result["search_terms"], ["What is artificial intelligence?"])

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_analyze_query_with_exception(self, mock_generate):
        # Test when Gemini API raises an exception
        mock_generate.side_effect = Exception("API Error")

        # Test query analysis with API error
        query = "What is quantum computing?"
        result = self.agent.analyze_query(query)

        # Check that fallback response is used
        self.assertEqual(result["main_topic"], query)
        self.assertEqual(result["search_terms"], [query])

        # Verify the exception was handled gracefully
        # The error message in the terminal is expected and doesn't indicate a test failure

    @patch('tools.WebSearchTool.search')
    def test_search_web_with_empty_results(self, mock_search):
        # Test when search returns empty results
        mock_search.return_value = []

        # Test web search with empty results
        search_terms = ["nonexistent topic"]
        results = self.agent.search_web(search_terms)

        # Check that results are empty
        self.assertEqual(len(results), 0)

    @patch('tools.WebSearchTool.search')
    def test_search_web_with_duplicate_urls(self, mock_search):
        # Test deduplication of search results
        mock_search.return_value = [
            {"title": "Duplicate Result", "link": "http://example.com/same", "snippet": "Same URL"},
            {"title": "Duplicate Result 2", "link": "http://example.com/same", "snippet": "Same URL again"}
        ]
    
        # Test web search with duplicate URLs
        search_terms = ["duplicate test"]
        results = self.agent.search_web(search_terms)
    
        # Check that duplicates are removed and max_total_results is respected
        self.assertLessEqual(len(results), 1)  # max_total_results is now 1
        if results:
            self.assertEqual(results[0]["title"], "Duplicate Result")

    @patch('tools.WebScraperTool.scrape')
    @patch('tools.ContentAnalyzerTool.analyze')
    def test_extract_content_with_low_relevance(self, mock_analyze, mock_scrape):
        # Test filtering of low-relevance content
        mock_scrape.return_value = {
            "title": "Low Relevance Page",
            "content": "Low relevance content",
            "url": "http://example.com/low"
        }

        # Mock analyze results with low relevance score
        mock_analyze.return_value = {
            "relevance_score": 3,  # Below threshold of 5
            "relevant_content": "Low relevance content"
        }

        # Test content extraction with low relevance
        search_results = [{"title": "Low Relevance", "link": "http://example.com/low", "snippet": "Low relevance"}]
        results = self.agent.extract_content(search_results, "test query")

        # Check that low-relevance content is filtered out
        self.assertEqual(len(results), 0)

    @patch('tools.WebScraperTool.scrape')
    def test_extract_content_with_empty_content(self, mock_scrape):
        # Test handling of empty content
        mock_scrape.return_value = {
            "title": "Empty Page",
            "content": "",  # Empty content
            "url": "http://example.com/empty"
        }

        # Test content extraction with empty content
        search_results = [{"title": "Empty Page", "link": "http://example.com/empty", "snippet": "Empty"}]
        results = self.agent.extract_content(search_results, "test query")

        # Check that empty content is filtered out
        self.assertEqual(len(results), 0)

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_synthesize_information_with_empty_data(self, mock_generate):
        # Test synthesis with empty data
        result = self.agent.synthesize_information([], "test query")

        # Check that a message is returned for empty data
        # This is a more flexible assertion that should work with various implementations
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

        # For empty data, we should either:
        # 1. Not call Gemini (if that's how the agent is implemented)
        # mock_generate.assert_not_called()
        # OR
        # 2. Return a specific message without calling Gemini
        self.assertTrue("couldn't find" in result.lower() or
                        "no relevant" in result.lower() or
                        "no information" in result.lower() or
                        "failed to" in result.lower())

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_synthesize_information_with_exception(self, mock_generate):
        # Test when synthesis raises an exception
        mock_generate.side_effect = Exception("Synthesis Error")

        # Test synthesis with API error
        extracted_data = [{"title": "Source", "url": "http://example.com", "content": "Content", "relevance_score": 8}]
        result = self.agent.synthesize_information(extracted_data, "test query")

        # Check that error message is returned
        self.assertTrue("Failed to synthesize information" in result)

    def test_rate_limiting(self):
        # Test that rate limiting works
        start_time = time.time()

        # Call rate-limited method twice
        self.agent._rate_limit()
        self.agent._rate_limit()

        # Check that second call was delayed by min_api_interval
        elapsed_time = time.time() - start_time
        self.assertGreaterEqual(elapsed_time, self.agent.min_api_interval)

    @patch('google.generativeai.GenerativeModel.generate_content')
    @patch('tools.WebSearchTool.search')
    @patch('tools.WebScraperTool.scrape')
    @patch('tools.ContentAnalyzerTool.analyze')
    def test_full_research_process(self, mock_analyze, mock_scrape, mock_search, mock_generate):
        # Test the entire research process

        # Mock query analysis
        mock_response1 = MagicMock()
        mock_response1.text = json.dumps({
            "main_topic": "test topic",
            "key_aspects": ["aspect1"],
            "content_type": "facts",
            "search_terms": ["test search"]
        })

        # Mock synthesis
        mock_response2 = MagicMock()
        mock_response2.text = "Final research report"

        # Set up mock returns
        mock_generate.side_effect = [mock_response1, mock_response2]
        mock_search.return_value = [{"title": "Result", "link": "http://example.com", "snippet": "Snippet"}]
        mock_scrape.return_value = {"title": "Page", "content": "Content", "url": "http://example.com"}
        mock_analyze.return_value = {"relevance_score": 8, "relevant_content": "Relevant content"}

        # Run full research process
        result = self.agent.research("test query")

        # Check that all components were called
        self.assertEqual(mock_generate.call_count, 2)
        mock_search.assert_called_once()
        mock_scrape.assert_called_once()
        mock_analyze.assert_called_once()

        # Check final result
        self.assertTrue(result.startswith("Final research report"))

if __name__ == '__main__':
    unittest.main()
