def test_liveness(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_readiness(client):
    resp = client.get("/api/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert "checks" in data
    assert "ready" in data
