import os
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.skipif(os.getenv("REMOTE_LLM_ENABLED", "false").lower() not in ("1","true","yes") or not os.getenv("OPENAI_API_KEY") or not os.getenv("OPENAI_MODEL"), reason="Remote LLM disabled or no credentials")
def test_unified_search_with_llm_escalation():
    client = TestClient(app)
    resp = client.post(
        "/api/v1/search/unified",
        json={
            "query": "Summarize latest AI assistant capabilities",
            "include_local": False,
            "include_web": True,
            "max_results": 2,
            "escalate_llm": True
        },
    )
    assert resp.status_code in (200, 503, 429)
    data = resp.json()
    # If allowed, used.llm may be true; structure should be present when included
    if isinstance(data, dict) and data.get("used", {}).get("llm"):
        llm_items = [it for it in data.get("items", []) if it.get("source") == "llm"]
        assert len(llm_items) >= 1