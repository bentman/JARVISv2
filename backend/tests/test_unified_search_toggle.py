import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from tests.mock_providers import MockTavilyProvider


def test_unified_search_local_only():
    client = TestClient(app)
    resp = client.post("/api/v1/search/unified", json={"query": "hello", "include_local": True, "include_web": False})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and isinstance(data["items"], list)
    assert data.get("web_used") is False

def test_unified_search_web_enabled():
    """Test web search with mock provider when real API keys aren't available"""
    client = TestClient(app)
    
    # If real search is enabled and has API keys, test normally
    if (os.getenv("SEARCH_ENABLED", "false").lower() in ("1", "true", "yes") and 
        os.getenv("SEARCH_API_KEY")):
        resp = client.post("/api/v1/search/unified", 
                          json={"query": "open source ai", "include_local": False, 
                               "include_web": True, "max_results": 2})
        assert resp.status_code in (200, 503)  # 503 if provider rejects credentials/quota
    else:
        # Use mock provider for testing
        mock_provider = MockTavilyProvider()
        with patch('app.core.config.settings.SEARCH_ENABLED', True):
            with patch('app.services.unified_search_service.unified_search_service.enabled', True):
                with patch('app.services.unified_search_service.unified_search_service.providers', 
                           {"tavily": mock_provider}):
                    # Mock privacy service to allow web search
                    with patch('app.services.privacy_service.privacy_service.get_settings', 
                               return_value={"privacy_level": "balanced"}):
                        resp = client.post("/api/v1/search/unified", 
                                          json={"query": "open source ai", "include_local": False, 
                                               "include_web": True, "max_results": 2})
                        assert resp.status_code == 200
                        data = resp.json()
                        assert "items" in data and isinstance(data["items"], list)
                        assert data.get("web_used") is True
                        # Should have mock results
                        web_items = [item for item in data["items"] if item.get("source") == "web"]
                        assert len(web_items) > 0
