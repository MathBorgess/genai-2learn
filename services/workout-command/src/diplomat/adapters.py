"""
Anti-corruption layer (diplomat) adapters.
Translates between external HTTP request data and internal domain objects.
"""
from __future__ import annotations

from typing import Any


def session_from_request(data: dict[str, Any]) -> dict[str, Any]:
    """Translate API request to internal session creation parameters."""
    return {
        "athlete_id": data.get("athlete_id"),
        "planned_workout": data.get("planned_workout"),
        "readiness_score": data.get("readiness_score"),
    }


def session_to_response(session) -> dict[str, Any]:
    """Translate internal WorkoutSession to API response."""
    return {
        "id": session.id,
        "athlete_id": session.athlete_id,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "status": session.status,
        "planned_workout": session.planned_workout,
        "readiness_score": session.readiness_score,
    }


def set_from_request(data: dict[str, Any]) -> dict[str, Any]:
    """Translate API request to internal set recording parameters."""
    return {
        "exercise_id": data.get("exercise_id"),
        "load_kg": data.get("load_kg"),
        "reps": data.get("reps"),
        "rir_reported": data.get("rir_reported"),
        "rpe_reported": data.get("rpe_reported"),
        "bpm_avg": data.get("bpm_avg"),
        "bpm_peak": data.get("bpm_peak"),
        "rest_seconds": data.get("rest_seconds"),
    }


def set_to_response(exercise_set) -> dict[str, Any]:
    """Translate internal ExerciseSet to API response."""
    return {
        "id": exercise_set.id,
        "session_id": exercise_set.session_id,
        "exercise_id": exercise_set.exercise_id,
        "load_kg": exercise_set.load_kg,
        "reps": exercise_set.reps,
        "rir_reported": exercise_set.rir_reported,
        "rpe_reported": exercise_set.rpe_reported,
        "bpm_avg": exercise_set.bpm_avg,
        "bpm_peak": exercise_set.bpm_peak,
        "rest_seconds": exercise_set.rest_seconds,
        "created_at": exercise_set.created_at.isoformat() if exercise_set.created_at else None,
    }
