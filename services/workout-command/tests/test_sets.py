def test_record_set_returns_201(client, mock_session_repo, mock_set_repo, mock_publisher):
    response = client.post(
        "/sessions/session-123/sets",
        json={
            "exercise_id": "squat",
            "load_kg": 100.0,
            "reps": 8,
            "rir_reported": 2.0,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["exercise_id"] == "squat"
    assert data["load_kg"] == 100.0
    mock_set_repo.save.assert_called_once()
    mock_publisher.publish.assert_called_once()


def test_record_set_invalid_load_returns_400(client, mock_session_repo):
    response = client.post(
        "/sessions/session-123/sets",
        json={
            "exercise_id": "squat",
            "load_kg": -10.0,
            "reps": 8,
        },
    )
    assert response.status_code == 400


def test_record_set_missing_fields_returns_400(client):
    response = client.post(
        "/sessions/session-123/sets",
        json={"exercise_id": "squat"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_record_set_session_not_found_returns_400(client, mock_session_repo):
    mock_session_repo.find_by_id.return_value = None
    response = client.post(
        "/sessions/nonexistent/sets",
        json={
            "exercise_id": "squat",
            "load_kg": 100.0,
            "reps": 8,
        },
    )
    assert response.status_code == 400


def test_record_set_invalid_reps_returns_400(client, mock_session_repo):
    response = client.post(
        "/sessions/session-123/sets",
        json={
            "exercise_id": "squat",
            "load_kg": 100.0,
            "reps": 100,
        },
    )
    assert response.status_code == 400
