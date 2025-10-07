import json
from fastapi.testclient import TestClient

from app.main import app
from app.services.budget_service import budget_service


def test_chat_budget_enforcement_blocks_when_over_limit():
    client = TestClient(app)

    # Configure budget to enforce with tiny daily limit and cost rate
    budget_service.set_config(daily_limit_usd=0.01, monthly_limit_usd=0.01, enforce=True, cost_per_token_usd=0.001)

    # Log an event to exceed daily limit
    budget_service.log_event(category="test", tokens_used=200, execution_time_sec=0.1)  # cost = 0.2 > 0.01

    # Attempt chat request (should be blocked before inference)
    resp = client.post("/api/v1/chat/send", json={"message": "hello", "mode": "chat", "stream": False})
    assert resp.status_code == 429
    data = resp.json()
    assert isinstance(data, dict)
    assert data.get("detail", {}).get("error") == "Budget limit exceeded"
