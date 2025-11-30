def test_logs_endpoint(client):
    resp = client.get("/api/logs/recent")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
