import os
import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_unified_search_local_only():
    client = TestClient(app)
    resp = client.post("/api/v1/search/unified", json={"query": "hello", "include_local": True, "include_web": False})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and isinstance(data["items"], list)
    assert data.get("web_used") is False

@pytest.mark.skipif(os.getenv("SEARCH_ENABLED", "false").lower() not in ("1","true","yes") or not os.getenv("SEARCH_API_KEY"), reason="Web search disabled or no API key")
def test_unified_search_web_enabled():
    client = TestClient(app)
    resp = client.post("/api/v1/search/unified", json={"query": "open source ai", "include_local": False, "include_web": True, "max_results": 2})
    assert resp.status_code in (200, 503)  # 503 if provider rejects credentials/quota
    # Do not assert payload due to provider variability