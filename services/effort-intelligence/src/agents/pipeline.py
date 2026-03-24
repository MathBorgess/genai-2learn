"""
AgentPipeline: Orchestrates validation -> effort estimation -> recommendation.
"""
from __future__ import annotations

from agents.validation_agent import ValidationAgent, validation_agent
from agents.effort_agent import EffortAgent, effort_agent
from agents.recommendation_agent import RecommendationAgent, recommendation_agent

MINIMUM_DATA_QUALITY = 0.3


def conservative_fallback(set_data: dict) -> dict:
    """Return a safe conservative result when data quality is too low."""
    return {
        "validation": {
            "data_quality_score": 0.0,
            "is_valid": False,
            "validity_flags": {},
            "missingness_profile": {},
            "warnings": ["Data quality too low for processing"],
        },
        "effort": {
            "effort_score": 50.0,
            "rir_estimate": 5.0,
            "confidence": 0.1,
            "feature_contributions": {},
        },
        "recommendation": {
            "action_type": "MAINTAIN",
            "load_delta_pct": 0.0,
            "cue_list": ["Please provide complete set data for accurate recommendations"],
            "safety_reason_codes": ["DATA_QUALITY_INSUFFICIENT"],
            "rationale": "Set data quality is too low for reliable analysis. Maintaining current load as a precaution.",
        },
        "correlation_id": set_data.get("correlation_id"),
        "fallback": True,
    }


class AgentPipeline:
    def __init__(
        self,
        _validation_agent: ValidationAgent | None = None,
        _effort_agent: EffortAgent | None = None,
        _recommendation_agent: RecommendationAgent | None = None,
    ) -> None:
        self._validation_agent = _validation_agent or validation_agent
        self._effort_agent = _effort_agent or effort_agent
        self._recommendation_agent = _recommendation_agent or recommendation_agent

    def run(self, set_data: dict) -> dict:
        # Step 1: Validate
        validation_result = self._validation_agent.validate(set_data)

        if validation_result["data_quality_score"] <= MINIMUM_DATA_QUALITY:
            return conservative_fallback(set_data)

        # Step 2: Estimate effort
        effort_result = self._effort_agent.estimate(set_data, validation_result)

        # Step 3: Generate recommendation
        recommendation = self._recommendation_agent.recommend(
            set_data, effort_result, validation_result
        )

        return {
            "validation": validation_result,
            "effort": effort_result,
            "recommendation": recommendation,
            "correlation_id": set_data.get("correlation_id"),
            "fallback": False,
        }
