import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_provider" in data
    assert "provider_health" in data

def test_providers_endpoint():
    response = client.get("/api/providers")
    assert response.status_code == 200
    data = response.json()
    assert "active_provider" in data
    assert "ollama" in data["available_providers"]

def test_session_lifecycle():
    # 1. Create Session
    create_res = client.post("/api/sessions", json={"title": "Test PM Session"})
    assert create_res.status_code == 201
    session_data = create_res.json()
    session_id = session_data["id"]
    assert session_data["title"] == "Test PM Session"

    # 2. Get Session Details
    get_res = client.get(f"/api/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == session_id

    # 3. List Sessions
    list_res = client.get("/api/sessions")
    assert list_res.status_code == 200
    session_ids = [s["id"] for s in list_res.json()]
    assert session_id in session_ids

    # 4. Delete Session
    del_res = client.delete(f"/api/sessions/{session_id}")
    assert del_res.status_code == 204

    # 5. Verify Deletion
    get_again = client.get(f"/api/sessions/{session_id}")
    assert get_again.status_code == 404
