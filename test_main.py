import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200

def test_chat_method_not_allowed():
    response = client.get("/chat")
    assert response.status_code == 405

def test_chat_invalid_payload():
    response = client.post("/chat", json={"wrong_key": "data"})
    assert response.status_code == 200 # Will return our custom error dict
