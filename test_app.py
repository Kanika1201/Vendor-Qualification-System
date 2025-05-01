'''
test_app.py

Unit tests for the FastAPI '/vendor_qualification' endpoint using TestClient.
Covers cases including:
- Valid category and capabilities
- Invalid category
- Empty capabilities

Run tests with:
    pytest

Author: Kanika Saxena
'''

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_valid_query():
    response = client.post(
        "/vendor_qualification",
        json={
            "software_category": "CRM Software",
            "capabilities": ["Lead Management"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "product_name" in data[0]
        assert "final_score" in data[0]

def test_invalid_category():
    response = client.post(
        "/vendor_qualification",
        json={
            "software_category": "Music",  
            "capabilities": ["Chords"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert "no vendors" in data["message"].lower()

def test_empty_capabilities():
    response = client.post(
        "/vendor_qualification",
        json={
            "software_category": "CRM Software",
            "capabilities": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get("message") == "No vendors found matching the criteria."
