from __future__ import annotations

import json

from domain.entities import WorkoutSession, ExerciseSet
from infrastructure.database import get_db_session
from sqlalchemy import text


class PostgresSessionRepository:
    def save(self, session: WorkoutSession) -> None:
        db = get_db_session()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO workout_sessions (id, athlete_id, started_at, status, planned_workout, readiness_score)
                    VALUES (:id, :athlete_id, :started_at, :status, :planned_workout::jsonb, :readiness_score)
                    ON CONFLICT (id) DO UPDATE
                    SET status = EXCLUDED.status
                    """
                ),
                {
                    "id": session.id,
                    "athlete_id": session.athlete_id,
                    "started_at": session.started_at,
                    "status": session.status,
                    "planned_workout": json.dumps(session.planned_workout) if session.planned_workout else None,
                    "readiness_score": session.readiness_score,
                },
            )
            db.commit()
        finally:
            db.close()

    def find_by_id(self, session_id: str) -> WorkoutSession | None:
        db = get_db_session()
        try:
            row = db.execute(
                text("SELECT id, athlete_id, started_at, status, planned_workout, readiness_score FROM workout_sessions WHERE id = :id"),
                {"id": session_id},
            ).fetchone()
            if row is None:
                return None
            return WorkoutSession(
                id=str(row.id),
                athlete_id=str(row.athlete_id),
                started_at=row.started_at,
                status=row.status,
                planned_workout=row.planned_workout,
                readiness_score=row.readiness_score,
            )
        finally:
            db.close()


class PostgresSetRepository:
    def save(self, exercise_set: ExerciseSet) -> None:
        db = get_db_session()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO exercise_sets (id, session_id, exercise_id, load_kg, reps, rir_reported, rpe_reported, bpm_avg, bpm_peak, rest_seconds, created_at)
                    VALUES (:id, :session_id, :exercise_id, :load_kg, :reps, :rir_reported, :rpe_reported, :bpm_avg, :bpm_peak, :rest_seconds, :created_at)
                    """
                ),
                {
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
                    "created_at": exercise_set.created_at,
                },
            )
            db.commit()
        finally:
            db.close()
