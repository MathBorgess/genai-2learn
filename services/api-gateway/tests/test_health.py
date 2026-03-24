def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "api-gateway"
    assert data["version"] == "1.0.0"
