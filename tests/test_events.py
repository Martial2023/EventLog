from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_event():
    response = client.post("/events", json={
        "user_id": "karmel",
        "occurred_at": "2026-01-21T14:30:00Z",
        "kind": "click",
        "tags": ["checkout"]
    })
    assert response.status_code == 201
    
def test_duplicated_event():
    response = client.post("/events", json={
        "user_id": "karmel",
        "occurred_at": "2026-01-21T14:30:00Z",
        "kind": "click",
        "tags": ["checkout"]
    })
    assert response.status_code == 409