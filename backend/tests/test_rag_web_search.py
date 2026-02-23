"""
Unit tests for WebRAG module
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_web_search import WebRAG, WebSearchResult


class TestWebRAG(unittest.TestCase):
    """Test cases for WebRAG"""

    def setUp(self):
        """Set up test instance with search mocked as unavailable"""
        self.rag = WebRAG(max_results=3, snippet_max_chars=200)

    # ------------------------------------------------------------------
    # should_search()
    # ------------------------------------------------------------------

    def test_should_search_with_what_is(self):
        """Queries starting with 'what is' should trigger a search"""
        self.assertTrue(self.rag.should_search("what is quantum computing?"))

    def test_should_search_with_latest(self):
        """Queries containing 'latest' should trigger a search"""
        self.assertTrue(self.rag.should_search("What is the latest AI news?"))

    def test_should_search_how_to(self):
        """Queries with 'how to' should trigger a search"""
        self.assertTrue(self.rag.should_search("how to bake a cake"))

    def test_should_search_casual_conversation(self):
        """Casual conversation should NOT trigger a search"""
        self.assertFalse(self.rag.should_search("hello!"))
        self.assertFalse(self.rag.should_search("you're so cute"))

    def test_should_search_case_insensitive(self):
        """should_search should be case-insensitive"""
        self.assertTrue(self.rag.should_search("WHAT IS the speed of light?"))

    # ------------------------------------------------------------------
    # format_context()
    # ------------------------------------------------------------------

    def test_format_context_empty(self):
        """Empty results produce an empty string"""
        self.assertEqual(self.rag.format_context([]), "")

    def test_format_context_single_result(self):
        """Single result is formatted with header and index"""
        results = [WebSearchResult(title="Test Title", body="Test body text.", href="https://example.com")]
        context = self.rag.format_context(results)

        self.assertIn("[Web Search Results]", context)
        self.assertIn("Test Title", context)
        self.assertIn("Test body text.", context)

    def test_format_context_multiple_results(self):
        """Multiple results are all included"""
        results = [
            WebSearchResult(title="Result 1", body="Body 1"),
            WebSearchResult(title="Result 2", body="Body 2"),
        ]
        context = self.rag.format_context(results)

        self.assertIn("Result 1", context)
        self.assertIn("Result 2", context)
        self.assertIn("1.", context)
        self.assertIn("2.", context)

    # ------------------------------------------------------------------
    # search() – mocking DDGS
    # ------------------------------------------------------------------

    def test_search_returns_empty_when_unavailable(self):
        """search() returns [] when duckduckgo_search is not installed"""
        rag = WebRAG()
        rag._ddgs_available = False
        results = rag.search("test query")
        self.assertEqual(results, [])

    def test_search_returns_results_when_ddgs_available(self):
        """search() returns WebSearchResult list when DDGS is available"""
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {"title": "T1", "body": "B1", "href": "https://a.com"},
            {"title": "T2", "body": "B2", "href": "https://b.com"},
        ]
        mock_ddgs_context = MagicMock()
        mock_ddgs_context.__enter__ = MagicMock(return_value=mock_ddgs_instance)
        mock_ddgs_context.__exit__ = MagicMock(return_value=False)

        rag = WebRAG.__new__(WebRAG)
        rag.max_results = 3
        rag.snippet_max_chars = 200
        rag._ddgs_available = True

        with patch("rag_web_search.DDGS", return_value=mock_ddgs_context, create=True):
            results = rag.search("test query")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "T1")
        self.assertEqual(results[1].title, "T2")

    def test_search_handles_exception_gracefully(self):
        """search() returns [] when DDGS raises an exception"""
        rag = WebRAG.__new__(WebRAG)
        rag.max_results = 3
        rag.snippet_max_chars = 200
        rag._ddgs_available = True

        with patch("rag_web_search.DDGS", side_effect=Exception("network error"), create=True):
            results = rag.search("test query")

        self.assertEqual(results, [])

    # ------------------------------------------------------------------
    # augment_query()
    # ------------------------------------------------------------------

    def test_augment_query_returns_none_for_casual_chat(self):
        """augment_query returns None when search is not needed"""
        result = self.rag.augment_query("hey, how are you?")
        self.assertIsNone(result)

    def test_augment_query_returns_none_when_search_empty(self):
        """augment_query returns None when search produces no results"""
        rag = WebRAG()
        rag._ddgs_available = False
        result = rag.augment_query("what is the weather today?")
        self.assertIsNone(result)

    def test_augment_query_returns_context_when_results_exist(self):
        """augment_query returns formatted context when results exist"""
        rag = WebRAG.__new__(WebRAG)
        rag.max_results = 3
        rag.snippet_max_chars = 200
        rag._ddgs_available = True

        mock_result = WebSearchResult("AI News", "Some AI news body text.", "https://news.com")

        with patch.object(rag, "search", return_value=[mock_result]):
            context = rag.augment_query("what is the latest AI news?")

        self.assertIsNotNone(context)
        self.assertIn("AI News", context)

    # ------------------------------------------------------------------
    # is_available property
    # ------------------------------------------------------------------

    def test_is_available_reflects_ddgs_flag(self):
        rag = WebRAG()
        rag._ddgs_available = True
        self.assertTrue(rag.is_available)
        rag._ddgs_available = False
        self.assertFalse(rag.is_available)

    # ------------------------------------------------------------------
    # snippet truncation
    # ------------------------------------------------------------------

    def test_snippet_truncated_to_max_chars(self):
        """Search results should be truncated to snippet_max_chars"""
        long_body = "x" * 500

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {"title": "T", "body": long_body, "href": "https://a.com"},
        ]
        mock_ddgs_context = MagicMock()
        mock_ddgs_context.__enter__ = MagicMock(return_value=mock_ddgs_instance)
        mock_ddgs_context.__exit__ = MagicMock(return_value=False)

        rag = WebRAG.__new__(WebRAG)
        rag.max_results = 3
        rag.snippet_max_chars = 200
        rag._ddgs_available = True

        with patch("rag_web_search.DDGS", return_value=mock_ddgs_context, create=True):
            results = rag.search("test")

        self.assertLessEqual(len(results[0].body), 200)


if __name__ == "__main__":
    unittest.main()
