import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import create_app
from config import Config
from domain.entities import EffortEstimate, Recommendation


class TestConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
    EXCHANGE_NAME = "test_exchange"


@pytest.fixture
def mock_estimate_repo():
    repo = MagicMock()
    repo.find_by_set_id.return_value = EffortEstimate(
        id="estimate-123",
        set_id="set-123",
        effort_score=75.0,
        rir_estimate=2.5,
        confidence=0.85,
        feature_contributions={"rir_reported": 1.0},
    )
    return repo


@pytest.fixture
def mock_recommendation_repo():
    repo = MagicMock()
    repo.find_by_set_id.return_value = Recommendation(
        id="rec-123",
        set_id="set-123",
        action_type="MAINTAIN",
        load_delta_pct=0.0,
        rationale="Test rationale",
    )
    return repo


@pytest.fixture
def mock_publisher():
    return MagicMock()


@pytest.fixture
def app(mock_estimate_repo, mock_recommendation_repo, mock_publisher):
    application = create_app(
        config=TestConfig,
        estimate_repo=mock_estimate_repo,
        recommendation_repo=mock_recommendation_repo,
        publisher=mock_publisher,
    )
    return application


@pytest.fixture
def client(app):
    return app.test_client()
