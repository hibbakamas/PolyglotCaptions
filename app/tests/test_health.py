from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert data.get("status") == "ok"
