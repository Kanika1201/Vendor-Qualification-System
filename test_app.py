from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_vendor_qualification():
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
    if data:  # If vendors are returned
        assert "product_name" in data[0]
        assert "final_score" in data[0]
