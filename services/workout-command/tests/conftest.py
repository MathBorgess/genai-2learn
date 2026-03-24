import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import MagicMock
from app import create_app
from config import Config
from domain.entities import WorkoutSession, ExerciseSet


class TestConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
    EXCHANGE_NAME = "test_exchange"


@pytest.fixture
def mock_session_repo():
    repo = MagicMock()
    repo.find_by_id.return_value = WorkoutSession(
        id="session-123",
        athlete_id="athlete-123",
    )
    return repo


@pytest.fixture
def mock_set_repo():
    return MagicMock()


@pytest.fixture
def mock_publisher():
    return MagicMock()


@pytest.fixture
def app(mock_session_repo, mock_set_repo, mock_publisher):
    application = create_app(
        config=TestConfig,
        session_repo=mock_session_repo,
        set_repo=mock_set_repo,
        publisher=mock_publisher,
    )
    return application


@pytest.fixture
def client(app):
    return app.test_client()
