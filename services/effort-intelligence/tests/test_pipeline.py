import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.pipeline import AgentPipeline, conservative_fallback


@pytest.fixture
def pipeline():
    return AgentPipeline()


def test_pipeline_full_flow_valid_data(pipeline):
    set_data = {
        "set_id": "set-abc-123",
        "exercise_id": "bench_press",
        "load_kg": 80.0,
        "reps": 8,
        "rir_reported": 3.0,
        "correlation_id": "corr-001",
    }
    result = pipeline.run(set_data)
    assert result["fallback"] is False
    assert "validation" in result
    assert "effort" in result
    assert "recommendation" in result
    assert result["correlation_id"] == "corr-001"
    assert result["effort"]["effort_score"] == 70.0
    assert result["recommendation"]["action_type"] in [
        "INCREASE_LOAD", "DECREASE_LOAD", "MAINTAIN", "ADJUST_TECHNIQUE"
    ]


def test_pipeline_low_quality_data_fallback(pipeline):
    set_data = {"correlation_id": "corr-002"}
    result = pipeline.run(set_data)
    assert result["fallback"] is True
    assert result["recommendation"]["action_type"] == "MAINTAIN"
    assert "DATA_QUALITY_INSUFFICIENT" in result["recommendation"]["safety_reason_codes"]
    assert result["correlation_id"] == "corr-002"


def test_pipeline_preserves_correlation_id(pipeline):
    set_data = {
        "exercise_id": "squat",
        "load_kg": 100.0,
        "reps": 5,
        "rir_reported": 4.0,
        "correlation_id": "my-special-corr-id",
    }
    result = pipeline.run(set_data)
    assert result["correlation_id"] == "my-special-corr-id"


def test_pipeline_pain_flag_respected(pipeline):
    set_data = {
        "exercise_id": "deadlift",
        "load_kg": 150.0,
        "reps": 5,
        "rir_reported": 3.0,
        "pain_flag": True,
        "correlation_id": "corr-pain",
    }
    result = pipeline.run(set_data)
    assert result["recommendation"]["action_type"] == "DECREASE_LOAD"
    assert "PAIN_FLAG_ACTIVE" in result["recommendation"]["safety_reason_codes"]


def test_pipeline_with_mocked_agents(pipeline):
    mock_validator = MagicMock()
    mock_validator.validate.return_value = {
        "data_quality_score": 0.85,
        "is_valid": True,
        "validity_flags": {},
        "missingness_profile": {},
        "warnings": [],
    }
    mock_effort = MagicMock()
    mock_effort.estimate.return_value = {
        "effort_score": 65.0,
        "rir_estimate": 3.5,
        "confidence": 0.75,
        "feature_contributions": {"rir_reported": 1.0},
    }
    mock_rec = MagicMock()
    mock_rec.recommend.return_value = {
        "action_type": "MAINTAIN",
        "load_delta_pct": 0.0,
        "cue_list": [],
        "safety_reason_codes": [],
        "rationale": "Mocked rationale",
    }
    p = AgentPipeline(
        _validation_agent=mock_validator,
        _effort_agent=mock_effort,
        _recommendation_agent=mock_rec,
    )
    result = p.run({"exercise_id": "squat", "load_kg": 80, "reps": 8})
    mock_validator.validate.assert_called_once()
    mock_effort.estimate.assert_called_once()
    mock_rec.recommend.assert_called_once()
    assert result["recommendation"]["action_type"] == "MAINTAIN"
