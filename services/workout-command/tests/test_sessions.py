from unittest.mock import MagicMock
from domain.entities import WorkoutSession


def test_create_session_returns_201(client, mock_session_repo, mock_publisher):
    response = client.post(
        "/sessions",
        json={"athlete_id": "athlete-123"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["status"] == "active"
    mock_session_repo.save.assert_called_once()
    mock_publisher.publish.assert_called_once()


def test_create_session_missing_athlete_id_returns_400(client):
    response = client.post("/sessions", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_get_session_returns_200(client, mock_session_repo):
    response = client.get("/sessions/session-123")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == "session-123"


def test_get_session_not_found_returns_404(client, mock_session_repo):
    mock_session_repo.find_by_id.return_value = None
    response = client.get("/sessions/nonexistent")
    assert response.status_code == 404


def test_create_session_with_readiness_score(client, mock_session_repo):
    response = client.post(
        "/sessions",
        json={"athlete_id": "athlete-123", "readiness_score": 8.5},
    )
    assert response.status_code == 201
