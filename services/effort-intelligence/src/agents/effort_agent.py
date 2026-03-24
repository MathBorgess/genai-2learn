"""
EffortAgent: Rule-based effort estimation using physiological signals.
"""
from __future__ import annotations

from typing import Any, Optional


DEFAULT_MAX_REPS = 12


class EffortAgent:
    def estimate(
        self,
        set_data: dict[str, Any],
        validation_result: dict[str, Any],
        history: Optional[list] = None,
    ) -> dict[str, Any]:
        data_quality = validation_result.get("data_quality_score", 0.5)
        feature_contributions: dict[str, float] = {}
        effort_score: float
        rir_estimate: float
        base_confidence: float

        rir_reported = set_data.get("rir_reported")
        rpe_reported = set_data.get("rpe_reported")
        reps = set_data.get("reps", 0)
        expected_max = set_data.get("expected_max_reps", DEFAULT_MAX_REPS)

        if rir_reported is not None:
            # Highest priority: direct athlete self-report
            rir_val = float(rir_reported)
            effort_score = (10.0 - rir_val) * 10.0
            rir_estimate = rir_val
            base_confidence = 0.8
            feature_contributions["rir_reported"] = 1.0

        elif rpe_reported is not None:
            # Secondary: RPE to RIR conversion
            rpe_val = float(rpe_reported)
            rir_estimate = max(10.0 - rpe_val, 0.0)
            effort_score = rpe_val * 10.0
            base_confidence = 0.65
            feature_contributions["rpe_reported"] = 1.0

        else:
            # Tertiary: rep ratio method
            rep_ratio = float(reps) / float(expected_max) if expected_max > 0 else 0.5
            effort_score = min(rep_ratio * 75.0, 95.0)
            rir_estimate = max((1.0 - rep_ratio) * 5.0, 0.0)
            base_confidence = 0.4
            feature_contributions["rep_ratio"] = rep_ratio

        # BPM as supplementary signal (never sole signal)
        bpm_avg = set_data.get("bpm_avg")
        if bpm_avg is not None:
            feature_contributions["bpm_signal"] = 0.2
            base_confidence = min(base_confidence + 0.1, 1.0)

        # Clamp effort score
        effort_score = max(0.0, min(100.0, effort_score))

        # Adjust confidence by data quality
        confidence = min(base_confidence * data_quality + base_confidence * 0.2, 1.0)
        # Ensure confidence is bounded
        confidence = max(0.0, min(1.0, confidence))

        return {
            "effort_score": round(effort_score, 2),
            "rir_estimate": round(rir_estimate, 2),
            "confidence": round(confidence, 3),
            "feature_contributions": feature_contributions,
        }


# Module-level singleton
effort_agent = EffortAgent()
