from unittest.mock import patch, MagicMock


def test_create_session_requires_auth(client):
    response = client.post("/api/v1/sessions", json={"athlete_id": "test"})
    assert response.status_code == 401


def test_create_session_with_valid_token(client, auth_headers):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "session-123", "status": "active"}
    mock_response.status_code = 201

    with patch("routes.sessions.requests.post", return_value=mock_response):
        response = client.post(
            "/api/v1/sessions",
            json={"athlete_id": "athlete-123"},
            headers=auth_headers,
        )
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == "session-123"


def test_get_session_with_valid_token(client, auth_headers):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "session-123", "status": "active"}
    mock_response.status_code = 200

    with patch("routes.sessions.requests.get", return_value=mock_response):
        response = client.get("/api/v1/sessions/session-123", headers=auth_headers)
    assert response.status_code == 200


def test_record_set_requires_auth(client):
    response = client.post("/api/v1/sessions/session-123/sets", json={})
    assert response.status_code == 401


def test_get_recommendation_requires_auth(client):
    response = client.get("/api/v1/recommendations/set-123")
    assert response.status_code == 401


def test_upstream_unavailable_returns_502(client, auth_headers):
    import requests as req_lib
    with patch("routes.sessions.requests.post", side_effect=req_lib.RequestException("connection refused")):
        response = client.post(
            "/api/v1/sessions",
            json={"athlete_id": "athlete-123"},
            headers=auth_headers,
        )
    assert response.status_code == 502


def test_missing_auth_header_returns_401(client):
    response = client.get("/api/v1/sessions/session-123")
    assert response.status_code == 401


def test_invalid_token_returns_401(client):
    response = client.get(
        "/api/v1/sessions/session-123",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
