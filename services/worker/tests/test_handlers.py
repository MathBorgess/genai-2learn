import sys
import os
import pytest
import json
from unittest.mock import MagicMock, patch
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from handlers.set_recorded import SetRecordedHandler
from handlers.dlq_handler import DLQHandler


@pytest.fixture
def set_recorded_handler(mock_orchestrator):
    return SetRecordedHandler(orchestrator=mock_orchestrator)


@pytest.fixture
def dlq_handler():
    return DLQHandler()


def test_set_recorded_handler_calls_pipeline(set_recorded_handler, mock_orchestrator):
    event = {
        "event_type": "set.recorded",
        "version": "1",
        "correlation_id": "corr-test-001",
        "causation_id": "cause-001",
        "timestamp": "2024-01-15T10:00:00Z",
        "payload": {
            "set_id": "set-abc",
            "session_id": "sess-123",
            "exercise_id": "squat",
            "load_kg": 100.0,
            "reps": 8,
            "rir_reported": 2.0,
        },
    }

    result = set_recorded_handler.handle(event)

    mock_orchestrator.process.assert_called_once()
    call_args = mock_orchestrator.process.call_args[0][0]
    assert call_args["exercise_id"] == "squat"
    assert call_args["load_kg"] == 100.0
    assert call_args["correlation_id"] == "corr-test-001"
    assert result["recommendation"]["action_type"] == "MAINTAIN"


def test_set_recorded_handler_injects_correlation_id(set_recorded_handler, mock_orchestrator):
    event = {
        "event_type": "set.recorded",
        "correlation_id": "unique-corr-xyz",
        "payload": {
            "set_id": "set-999",
            "exercise_id": "bench_press",
            "load_kg": 80.0,
            "reps": 10,
        },
    }
    set_recorded_handler.handle(event)
    call_args = mock_orchestrator.process.call_args[0][0]
    assert call_args["correlation_id"] == "unique-corr-xyz"


def test_set_recorded_handler_handles_empty_payload(set_recorded_handler, mock_orchestrator):
    event = {
        "event_type": "set.recorded",
        "correlation_id": "corr-empty",
        "payload": {},
    }
    result = set_recorded_handler.handle(event)
    assert result is not None
    mock_orchestrator.process.assert_called_once()


def test_dlq_handler_logs_error(dlq_handler, caplog):
    message = {
        "event_type": "set.recorded",
        "correlation_id": "corr-failed",
        "payload": {"set_id": "set-failed"},
    }
    with caplog.at_level(logging.ERROR):
        dlq_handler.handle(json.dumps(message).encode("utf-8"))

    assert "DLQ message received" in caplog.text
    assert "corr-failed" in caplog.text


def test_dlq_handler_handles_invalid_json(dlq_handler, caplog):
    with caplog.at_level(logging.ERROR):
        dlq_handler.handle(b"not valid json {{{")
    assert "Could not parse message body" in caplog.text


def test_dlq_handler_logs_death_info(dlq_handler, caplog):
    message = {
        "event_type": "set.recorded",
        "correlation_id": "corr-death",
        "payload": {},
    }
    headers = {
        "x-death": [
            {"queue": "set.recorded", "reason": "rejected", "count": 3}
        ]
    }
    with caplog.at_level(logging.ERROR):
        dlq_handler.handle(json.dumps(message).encode("utf-8"), headers=headers)
    assert "Death info" in caplog.text
    assert "rejected" in caplog.text
