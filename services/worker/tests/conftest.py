import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config


class TestConfig(Config):
    RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
    EFFORT_INTELLIGENCE_URL = "http://mock-effort-intelligence:8002"


@pytest.fixture
def mock_orchestrator():
    orchestrator = MagicMock()
    orchestrator.process.return_value = {
        "validation": {"data_quality_score": 0.9},
        "effort": {
            "effort_score": 70.0,
            "rir_estimate": 3.0,
            "confidence": 0.85,
            "feature_contributions": {"rir_reported": 1.0},
        },
        "recommendation": {
            "action_type": "MAINTAIN",
            "load_delta_pct": 0.0,
            "cue_list": [],
            "safety_reason_codes": [],
            "rationale": "Optimal training zone.",
        },
        "correlation_id": "test-corr-id",
        "fallback": False,
    }
    return orchestrator
