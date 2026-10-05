import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from app import app


def test_dashboard():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"ShopNova Logistics Platform" in response.data
    assert b"SHIP001" in response.data


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert data["application"] == "shopnova-logistics"
    assert data["shipments_loaded"] == 5


def test_readiness_endpoint():
    client = app.test_client()
    response = client.get("/ready")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "ready"


def test_shipments_api():
    client = app.test_client()
    response = client.get("/api/shipments")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 5
    assert len(data["shipments"]) == 5


def test_existing_shipment_tracking():
    client = app.test_client()
    response = client.get("/api/shipments/SHIP002")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["shipment"]["shipment_id"] == "SHIP002"
    assert data["shipment"]["product"] == "Laptop"


def test_invalid_shipment_tracking():
    client = app.test_client()
    response = client.get("/api/shipments/SHIP999")
    data = response.get_json()

    assert response.status_code == 404
    assert data["status"] == "error"
