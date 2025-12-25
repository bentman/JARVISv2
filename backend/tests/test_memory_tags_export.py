from fastapi.testclient import TestClient
from app.main import app
from app.services.memory_service import memory_service

def test_memory_tags_and_export_import_roundtrip():
    client = TestClient(app)
    # Create convo and messages
    conv = memory_service.store_conversation("Tagged Conversation")
    m1 = memory_service.add_message(conv.id, "user", "hello world", tokens=2)
    m2 = memory_service.add_message(conv.id, "assistant", "hi!", tokens=1)

    # Tag the conversation
    r = client.post(f"/api/v1/memory/conversation/{conv.id}/tags", json={"tags": ["project", "urgent"]})
    assert r.status_code == 200

    # Filter by tags
    r = client.get("/api/v1/memory/conversations/by-tags", params={"tags": "project,urgent"})
    assert r.status_code == 200
    data = r.json()
    assert any(c["id"] == conv.id for c in data)

    # Export
    r = client.get("/api/v1/memory/export", params={"format": "json"})
    assert r.status_code == 200
    exported = r.json()
    assert "conversations" in exported and "messages" in exported

    # Import into new IDs (merge=false)
    r = client.post("/api/v1/memory/import", json={"conversations": exported["conversations"], "messages": exported["messages"], "merge": False})
    assert r.status_code == 200
    stats = r.json()
    assert stats["conversations"] >= 1 and stats["messages"] >= 2
