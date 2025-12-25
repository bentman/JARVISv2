"""
Mock providers for testing external services without real API keys
"""
from typing import List, Dict, Any, Optional
from app.services.search_providers import WebSearchProvider
from app.services.external_llm_providers import RemoteLLMProvider


class MockTavilyProvider(WebSearchProvider):
    """Mock Tavily search provider for testing"""
    
    def __init__(self, api_key: str = "test-key"):
        self.api_key = api_key
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Mock AI Assistant Test Result",
                "url": "https://example.com/mock-result-1",
                "snippet": "This is a mock search result for testing purposes. It simulates AI assistant capabilities."
            },
            {
                "title": "Another Mock Result",
                "url": "https://example.com/mock-result-2", 
                "snippet": "Second mock result demonstrating search functionality in test environment."
            }
        ][:max_results]


class MockOpenAIProvider(RemoteLLMProvider):
    """Mock OpenAI provider for testing LLM escalation"""
    
    def __init__(self, api_key: str = "test-key", model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
    
    def summarize(self, query: str, items: List[Dict], max_tokens: int = 512) -> Dict[str, Any]:
        # Generate a mock summary based on the input
        item_titles = [item.get("title", "Item") for item in items[:3]]
        mock_summary = f"Mock LLM Summary: Based on the query '{query}', the search results about {', '.join(item_titles)} suggest comprehensive capabilities in AI assistance including natural language processing, search integration, and contextual responses."
        
        return {
            "answer": mock_summary,
            "model_used": self.model,
            "tokens_used": len(mock_summary.split()) * 1.3  # rough token estimate
        }