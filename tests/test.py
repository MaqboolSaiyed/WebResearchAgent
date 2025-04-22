import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import WebResearchAgent
from tools import WebSearchTool, WebScraperTool, ContentAnalyzerTool, NewsAggregatorTool

class TestWebResearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = WebResearchAgent()

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

        # Check that search was called correctly
        mock_search.assert_called_once_with("test query")

        # Check result structure
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Test Result 1")
        self.assertEqual(results[1]["link"], "http://example.com/2")

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
        self.assertEqual(len(results), 1)
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
        self.assertIn("Source 2 - http://example.com/2", result)

if __name__ == '__main__':
    unittest.main()
