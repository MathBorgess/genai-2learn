"""
RecommendationAgent: Policy-based load recommendations with safety guardrails.

Safety rules are NON-NEGOTIABLE and override all other logic.
"""
from __future__ import annotations

from typing import Any

# Confidence tier thresholds
HIGH_CONFIDENCE = 0.7
MEDIUM_CONFIDENCE = 0.4


class RecommendationAgent:
    def recommend(
        self,
        set_data: dict[str, Any],
        effort_result: dict[str, Any],
        validation_result: dict[str, Any],
    ) -> dict[str, Any]:
        effort_score = effort_result["effort_score"]
        confidence = effort_result["confidence"]
        rir_estimate = effort_result["rir_estimate"]
        pain_flag = set_data.get("pain_flag", False)
        safety_reason_codes: list[str] = []

        # === SAFETY GUARDRAILS (Non-negotiable, checked first) ===

        # GUARDRAIL-001: Pain signal - always decrease
        if pain_flag:
            safety_reason_codes.append("PAIN_FLAG_ACTIVE")
            return self._build_response(
                action_type="DECREASE_LOAD",
                load_delta_pct=-10.0,
                cue_list=["Stop if pain worsens", "Consult a professional if pain persists"],
                safety_reason_codes=safety_reason_codes,
                rationale="Pain was reported. Load has been reduced for safety. Please consult a professional if pain persists.",
            )

        # GUARDRAIL-002: Maximum effort threshold
        if effort_score > 95:
            safety_reason_codes.append("MAX_EFFORT_THRESHOLD")
            return self._build_response(
                action_type="DECREASE_LOAD",
                load_delta_pct=-10.0,
                cue_list=["Reduce load on next set", "Prioritize recovery"],
                safety_reason_codes=safety_reason_codes,
                rationale=f"Your effort level ({effort_score:.0f}/100) was at maximum. Reducing load to prevent injury.",
            )

        # GUARDRAIL-003: Low confidence - always maintain
        if confidence < MEDIUM_CONFIDENCE:
            safety_reason_codes.append("LOW_CONFIDENCE_FALLBACK")
            return self._build_response(
                action_type="MAINTAIN",
                load_delta_pct=0.0,
                cue_list=["Report your Reps in Reserve (RIR) for better recommendations"],
                safety_reason_codes=safety_reason_codes,
                rationale="Insufficient data for a confident recommendation. Maintaining current load as a precaution.",
            )

        # === CONFIDENCE-TIERED RECOMMENDATION LOGIC ===

        if confidence >= HIGH_CONFIDENCE:
            return self._high_confidence_recommendation(
                effort_score, confidence, rir_estimate, safety_reason_codes
            )
        else:
            # MEDIUM confidence (0.4 <= confidence < 0.7)
            return self._medium_confidence_recommendation(
                effort_score, confidence, safety_reason_codes
            )

    def _high_confidence_recommendation(
        self,
        effort_score: float,
        confidence: float,
        rir_estimate: float,
        safety_reason_codes: list[str],
    ) -> dict[str, Any]:
        if effort_score < 40:
            return self._build_response(
                action_type="INCREASE_LOAD",
                load_delta_pct=5.0,
                cue_list=["You have plenty of reserve - increase the load", "Aim for RIR 2-3"],
                safety_reason_codes=safety_reason_codes,
                rationale=f"Your effort level ({effort_score:.0f}/100) is low with high confidence. Increasing load by 5%.",
            )
        elif effort_score < 60:
            return self._build_response(
                action_type="INCREASE_LOAD",
                load_delta_pct=2.5,
                cue_list=["Moderate increase available", "Monitor RIR on next set"],
                safety_reason_codes=safety_reason_codes,
                rationale=f"Your effort level ({effort_score:.0f}/100) has room for a small increase.",
            )
        elif effort_score <= 80:
            return self._build_response(
                action_type="MAINTAIN",
                load_delta_pct=0.0,
                cue_list=["Great effort level - stay here", "Focus on quality reps"],
                safety_reason_codes=safety_reason_codes,
                rationale=f"Your effort level ({effort_score:.0f}/100) is in the optimal training zone. Maintain current load.",
            )
        else:
            # effort 80-95
            return self._build_response(
                action_type="DECREASE_LOAD",
                load_delta_pct=-5.0,
                cue_list=["Reduce load slightly", "Aim for RIR 2-3 on next set"],
                safety_reason_codes=safety_reason_codes,
                rationale=f"Your effort level ({effort_score:.0f}/100) is high. Reducing load slightly for sustainable training.",
            )

    def _medium_confidence_recommendation(
        self,
        effort_score: float,
        confidence: float,
        safety_reason_codes: list[str],
    ) -> dict[str, Any]:
        # Medium confidence: only MAINTAIN or conservative DECREASE
        # NEVER INCREASE_LOAD in medium confidence tier
        if effort_score > 80:
            return self._build_response(
                action_type="DECREASE_LOAD",
                load_delta_pct=-5.0,
                cue_list=["Effort appears high - reduce load", "Report RIR for better guidance"],
                safety_reason_codes=safety_reason_codes,
                rationale=f"Effort appears high ({effort_score:.0f}/100) but confidence is moderate. Reducing load conservatively.",
            )
        return self._build_response(
            action_type="MAINTAIN",
            load_delta_pct=0.0,
            cue_list=["Report your RIR for more precise recommendations"],
            safety_reason_codes=safety_reason_codes,
            rationale=f"Confidence is moderate. Maintaining load as a safe default.",
        )

    def _build_response(
        self,
        action_type: str,
        load_delta_pct: float,
        cue_list: list[str],
        safety_reason_codes: list[str],
        rationale: str,
    ) -> dict[str, Any]:
        return {
            "action_type": action_type,
            "load_delta_pct": load_delta_pct,
            "cue_list": cue_list,
            "safety_reason_codes": safety_reason_codes,
            "rationale": rationale,
        }


# Module-level singleton
recommendation_agent = RecommendationAgent()
