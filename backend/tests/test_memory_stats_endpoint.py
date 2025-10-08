from fastapi.testclient import TestClient
from app.main import app
from app.services.memory_service import memory_service

def test_memory_stats_endpoint():
    client = TestClient(app)
    # Create conversation and messages directly via service
    conv = memory_service.store_conversation("Test Conversation")
    memory_service.add_message(conv.id, role="user", content="hello", tokens=3)
    memory_service.add_message(conv.id, role="assistant", content="world", tokens=5)

    resp = client.get(f"/api/v1/memory/stats/{conv.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["conversation_id"] == conv.id
    assert data["total_messages"] >= 2
    assert data["total_tokens"] >= 8