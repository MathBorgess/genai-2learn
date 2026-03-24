"""
ValidationAgent: Rule-based data quality and plausibility checks.
"""
from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = ("exercise_id", "load_kg", "reps")
OPTIONAL_SIGNAL_FIELDS = ("rir_reported", "rpe_reported", "bpm_avg", "bpm_peak")

# Physiological bounds
BOUNDS = {
    "reps": (1, 50),
    "load_kg": (0.5, 500),
    "bpm_avg": (40, 220),
    "bpm_peak": (40, 220),
    "rir_reported": (0, 10),
    "rpe_reported": (1, 10),
}


class ValidationAgent:
    def validate(self, set_data: dict[str, Any]) -> dict[str, Any]:
        flags: dict[str, bool] = {}
        warnings: list[str] = []

        # Check required fields
        has_required = all(
            set_data.get(f) is not None for f in REQUIRED_FIELDS
        )
        flags["has_required_fields"] = has_required

        # Validate physiological bounds
        for field, (lo, hi) in BOUNDS.items():
            value = set_data.get(field)
            if value is not None:
                in_bounds = lo <= float(value) <= hi
                flags[f"{field}_plausible"] = in_bounds
                if not in_bounds:
                    warnings.append(
                        f"{field}={value} is outside plausible range [{lo}, {hi}]"
                    )
            else:
                flags[f"{field}_plausible"] = True  # absent = not implausible

        # Special check: bpm_peak >= bpm_avg
        bpm_avg = set_data.get("bpm_avg")
        bpm_peak = set_data.get("bpm_peak")
        if bpm_avg is not None and bpm_peak is not None:
            if float(bpm_peak) < float(bpm_avg):
                flags["bpm_peak_plausible"] = False
                warnings.append("bpm_peak must be >= bpm_avg")

        # Physiologically implausible combination
        reps = set_data.get("reps")
        load = set_data.get("load_kg")
        if reps is not None and load is not None:
            if float(reps) > 30 and float(load) > 200:
                warnings.append("reps > 30 with load > 200kg is physiologically implausible")
                flags["reps_plausible"] = False

        # Missingness profile
        missingness: dict[str, bool] = {
            f: set_data.get(f) is None for f in OPTIONAL_SIGNAL_FIELDS
        }

        # Data quality score
        score = self._compute_quality_score(set_data, flags, missingness)

        return {
            "data_quality_score": score,
            "is_valid": has_required and all(
                v for k, v in flags.items() if "plausible" in k
            ),
            "validity_flags": flags,
            "missingness_profile": missingness,
            "warnings": warnings,
        }

    def _compute_quality_score(
        self,
        set_data: dict,
        flags: dict,
        missingness: dict,
    ) -> float:
        score = 0.0

        if flags.get("has_required_fields"):
            score += 0.4

        plausibility_flags = [v for k, v in flags.items() if "plausible" in k]
        if plausibility_flags:
            plausible_ratio = sum(plausibility_flags) / len(plausibility_flags)
            score += 0.3 * plausible_ratio

        # Bonus for optional signals
        present_signals = sum(1 for missing in missingness.values() if not missing)
        score += 0.075 * present_signals  # up to 0.3 for 4 signals

        return min(round(score, 3), 1.0)


# Module-level singleton
validation_agent = ValidationAgent()
