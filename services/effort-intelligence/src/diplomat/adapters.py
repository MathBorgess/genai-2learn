"""Anti-corruption layer adapters for effort-intelligence service."""
from __future__ import annotations
from typing import Any


def estimate_to_response(estimate) -> dict[str, Any]:
    return {
        "id": estimate.id,
        "set_id": estimate.set_id,
        "effort_score": estimate.effort_score,
        "rir_estimate": estimate.rir_estimate,
        "confidence": estimate.confidence,
        "feature_contributions": estimate.feature_contributions,
        "created_at": estimate.created_at.isoformat() if estimate.created_at else None,
    }


def recommendation_to_response(recommendation) -> dict[str, Any]:
    return {
        "id": recommendation.id,
        "set_id": recommendation.set_id,
        "action_type": recommendation.action_type,
        "load_delta_pct": recommendation.load_delta_pct,
        "cue_list": recommendation.cue_list,
        "safety_reason_codes": recommendation.safety_reason_codes,
        "rationale": recommendation.rationale,
        "created_at": recommendation.created_at.isoformat() if recommendation.created_at else None,
    }
