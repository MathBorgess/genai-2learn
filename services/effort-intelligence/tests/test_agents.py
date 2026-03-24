import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.validation_agent import ValidationAgent
from agents.effort_agent import EffortAgent
from agents.recommendation_agent import RecommendationAgent


@pytest.fixture
def validator():
    return ValidationAgent()


@pytest.fixture
def effort():
    return EffortAgent()


@pytest.fixture
def recommender():
    return RecommendationAgent()


@pytest.fixture
def good_validation():
    return {
        "data_quality_score": 0.9,
        "is_valid": True,
        "validity_flags": {"has_required_fields": True},
        "missingness_profile": {},
        "warnings": [],
    }


def test_validation_agent_valid_data(validator):
    result = validator.validate({
        "exercise_id": "squat",
        "load_kg": 100.0,
        "reps": 8,
        "rir_reported": 2.0,
        "bpm_avg": 140.0,
    })
    assert result["is_valid"] is True
    assert result["data_quality_score"] > 0.5
    assert result["validity_flags"]["has_required_fields"] is True


def test_validation_agent_missing_fields(validator):
    result = validator.validate({"exercise_id": "squat"})
    assert result["validity_flags"]["has_required_fields"] is False
    assert result["data_quality_score"] < 0.5


def test_validation_agent_invalid_bpm(validator):
    result = validator.validate({
        "exercise_id": "squat",
        "load_kg": 100.0,
        "reps": 8,
        "bpm_avg": 300.0,
    })
    assert result["validity_flags"]["bpm_avg_plausible"] is False
    assert len(result["warnings"]) > 0


def test_validation_agent_bpm_peak_less_than_avg(validator):
    result = validator.validate({
        "exercise_id": "squat",
        "load_kg": 100.0,
        "reps": 8,
        "bpm_avg": 160.0,
        "bpm_peak": 140.0,
    })
    assert result["validity_flags"]["bpm_peak_plausible"] is False


def test_validation_agent_implausible_combination(validator):
    result = validator.validate({
        "exercise_id": "squat",
        "load_kg": 250.0,
        "reps": 35,
    })
    assert result["validity_flags"]["reps_plausible"] is False


def test_effort_agent_with_rir_reported(effort, good_validation):
    result = effort.estimate(
        {"exercise_id": "squat", "load_kg": 100, "reps": 8, "rir_reported": 2.0},
        good_validation,
    )
    assert result["effort_score"] == 80.0
    assert result["rir_estimate"] == 2.0
    assert result["confidence"] > 0.5
    assert "rir_reported" in result["feature_contributions"]


def test_effort_agent_rir_zero_gives_100_effort(effort, good_validation):
    result = effort.estimate(
        {"exercise_id": "squat", "load_kg": 100, "reps": 8, "rir_reported": 0.0},
        good_validation,
    )
    assert result["effort_score"] == 100.0


def test_effort_agent_without_rir_reported(effort, good_validation):
    result = effort.estimate(
        {"exercise_id": "squat", "load_kg": 100, "reps": 8},
        good_validation,
    )
    assert "rep_ratio" in result["feature_contributions"]
    assert 0 <= result["effort_score"] <= 100


def test_effort_agent_uses_rep_ratio(effort, good_validation):
    result = effort.estimate(
        {"exercise_id": "squat", "load_kg": 80, "reps": 12},
        good_validation,
    )
    assert result["effort_score"] == 75.0
    assert "rep_ratio" in result["feature_contributions"]


def test_effort_agent_with_rpe_reported(effort, good_validation):
    result = effort.estimate(
        {"exercise_id": "squat", "load_kg": 100, "reps": 8, "rpe_reported": 8.0},
        good_validation,
    )
    assert result["effort_score"] == 80.0
    assert "rpe_reported" in result["feature_contributions"]


def test_effort_agent_confidence_bounded(effort, good_validation):
    result = effort.estimate(
        {"exercise_id": "squat", "load_kg": 100, "reps": 8, "rir_reported": 3.0},
        good_validation,
    )
    assert 0.0 <= result["confidence"] <= 1.0


def test_recommendation_agent_high_confidence_low_effort_increases_load(recommender):
    result = recommender.recommend(
        set_data={"pain_flag": False},
        effort_result={"effort_score": 35.0, "confidence": 0.85, "rir_estimate": 6.5},
        validation_result={"data_quality_score": 0.9},
    )
    assert result["action_type"] == "INCREASE_LOAD"
    assert result["load_delta_pct"] > 0


def test_recommendation_agent_low_confidence_always_maintains(recommender):
    result = recommender.recommend(
        set_data={"pain_flag": False},
        effort_result={"effort_score": 35.0, "confidence": 0.2, "rir_estimate": 6.5},
        validation_result={"data_quality_score": 0.9},
    )
    assert result["action_type"] == "MAINTAIN"
    assert "LOW_CONFIDENCE_FALLBACK" in result["safety_reason_codes"]


def test_recommendation_agent_high_effort_decreases_load(recommender):
    result = recommender.recommend(
        set_data={"pain_flag": False},
        effort_result={"effort_score": 96.0, "confidence": 0.9, "rir_estimate": 0.4},
        validation_result={"data_quality_score": 0.9},
    )
    assert result["action_type"] == "DECREASE_LOAD"
    assert "MAX_EFFORT_THRESHOLD" in result["safety_reason_codes"]


def test_recommendation_agent_never_increases_with_low_confidence(recommender):
    result = recommender.recommend(
        set_data={"pain_flag": False},
        effort_result={"effort_score": 20.0, "confidence": 0.5, "rir_estimate": 8.0},
        validation_result={"data_quality_score": 0.9},
    )
    assert result["action_type"] != "INCREASE_LOAD"


def test_recommendation_agent_pain_flag_always_decreases(recommender):
    result = recommender.recommend(
        set_data={"pain_flag": True},
        effort_result={"effort_score": 50.0, "confidence": 0.9, "rir_estimate": 5.0},
        validation_result={"data_quality_score": 0.9},
    )
    assert result["action_type"] == "DECREASE_LOAD"
    assert "PAIN_FLAG_ACTIVE" in result["safety_reason_codes"]


def test_recommendation_agent_optimal_effort_maintains(recommender):
    result = recommender.recommend(
        set_data={"pain_flag": False},
        effort_result={"effort_score": 70.0, "confidence": 0.8, "rir_estimate": 3.0},
        validation_result={"data_quality_score": 0.9},
    )
    assert result["action_type"] == "MAINTAIN"
