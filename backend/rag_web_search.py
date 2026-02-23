"""
RAG (Retrieval-Augmented Generation) with web search for Lucy AI Companion
Uses DuckDuckGo for free, no-API-key web search to augment LLM context
"""

import re
from typing import List, Optional
from dataclasses import dataclass

# Optional dependency – RAG is silently disabled when not installed
try:
    from duckduckgo_search import DDGS
    _DDGS_AVAILABLE = True
except ImportError:
    DDGS = None  # type: ignore[assignment,misc]
    _DDGS_AVAILABLE = False


@dataclass
class WebSearchResult:
    """Represents a single web search result"""
    title: str
    body: str
    href: str = ""


class WebRAG:
    """Web-based RAG for augmenting LLM context with current information"""

    # Trigger phrases that suggest web search would be helpful
    SEARCH_TRIGGERS = [
        "what is", "who is", "when is", "where is", "how to",
        "latest", "recent", "current", "today", "news",
        "what's", "who's", "define", "explain", "tell me about",
        "weather", "price", "score", "search", "find out",
    ]

    def __init__(self, max_results: int = 3, snippet_max_chars: int = 300):
        """
        Initialize WebRAG

        Args:
            max_results: Maximum number of search results to retrieve
            snippet_max_chars: Maximum characters per result snippet
        """
        self.max_results = max_results
        self.snippet_max_chars = snippet_max_chars
        self._ddgs_available = _DDGS_AVAILABLE

        if not self._ddgs_available:
            print("Warning: duckduckgo-search not installed. RAG web search will be unavailable.")

    @property
    def is_available(self) -> bool:
        """Return True if web search backend is available"""
        return self._ddgs_available

    def search(self, query: str) -> List[WebSearchResult]:
        """
        Search the web for a query using DuckDuckGo

        Args:
            query: Search query

        Returns:
            List of WebSearchResult objects
        """
        if not self._ddgs_available or DDGS is None:
            return []

        try:
            results: List[WebSearchResult] = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=self.max_results):
                    results.append(WebSearchResult(
                        title=r.get("title", ""),
                        body=r.get("body", "")[:self.snippet_max_chars],
                        href=r.get("href", "")
                    ))
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def format_context(self, results: List[WebSearchResult]) -> str:
        """
        Format search results as a context block for the LLM

        Args:
            results: List of search results

        Returns:
            Formatted context string ready to prepend to a system prompt
        """
        if not results:
            return ""

        context_parts = ["[Web Search Results]"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"{i}. {result.title}: {result.body}")

        return "\n".join(context_parts)

    def should_search(self, query: str) -> bool:
        """
        Heuristically decide whether a query needs web search

        Args:
            query: User query

        Returns:
            True if web search would likely improve the response
        """
        query_lower = query.lower()
        return any(trigger in query_lower for trigger in self.SEARCH_TRIGGERS)

    def augment_query(self, query: str) -> Optional[str]:
        """
        Return web-search context for the query when relevant, otherwise None

        Args:
            query: User query

        Returns:
            Context string to prepend, or None if search is not needed
        """
        if not self.should_search(query):
            return None

        results = self.search(query)
        if not results:
            return None

        return self.format_context(results)


# Example usage
if __name__ == "__main__":
    rag = WebRAG(max_results=3)

    query = "What is the latest news about AI?"
    print(f"Query: {query}")
    print(f"Should search: {rag.should_search(query)}")

    context = rag.augment_query(query)
    if context:
        print(f"Context:\n{context}")
    else:
        print("No context retrieved.")

