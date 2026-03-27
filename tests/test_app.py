from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] in {"sample", "pinot"}


def test_kpi_endpoint():
    response = client.get("/api/v1/kpis?window_minutes=120")
    assert response.status_code == 200
    body = response.json()
    assert "completed_trips" in body
    assert "gross_merchandise_value" in body


def test_trip_endpoint():
    response = client.get("/api/v1/trips/trip_000001")
    assert response.status_code in {200, 404}
