from __future__ import annotations

from typing import Protocol
from domain.entities import WorkoutSession, ExerciseSet
from domain.events import SessionStarted, SetRecorded


class SessionRepository(Protocol):
    def save(self, session: WorkoutSession) -> None: ...
    def find_by_id(self, session_id: str) -> WorkoutSession | None: ...


class SetRepository(Protocol):
    def save(self, exercise_set: ExerciseSet) -> None: ...


class EventPublisher(Protocol):
    def publish(self, routing_key: str, event_json: str) -> None: ...


class StartSessionUseCase:
    def __init__(
        self, session_repo: SessionRepository, publisher: EventPublisher
    ) -> None:
        self._session_repo = session_repo
        self._publisher = publisher

    def execute(self, athlete_id: str, planned_workout: dict | None = None, readiness_score: float | None = None) -> WorkoutSession:
        session = WorkoutSession(
            athlete_id=athlete_id,
            planned_workout=planned_workout,
            readiness_score=readiness_score,
        )
        self._session_repo.save(session)
        event = SessionStarted(session_id=session.id, athlete_id=session.athlete_id)
        self._publisher.publish("session.started", event.to_json())
        return session


class RecordSetUseCase:
    def __init__(
        self,
        session_repo: SessionRepository,
        set_repo: SetRepository,
        publisher: EventPublisher,
    ) -> None:
        self._session_repo = session_repo
        self._set_repo = set_repo
        self._publisher = publisher

    def execute(self, session_id: str, set_data: dict) -> ExerciseSet:
        session = self._session_repo.find_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        exercise_set = ExerciseSet(
            session_id=session_id,
            exercise_id=set_data["exercise_id"],
            load_kg=float(set_data["load_kg"]),
            reps=int(set_data["reps"]),
            rir_reported=set_data.get("rir_reported"),
            rpe_reported=set_data.get("rpe_reported"),
            bpm_avg=set_data.get("bpm_avg"),
            bpm_peak=set_data.get("bpm_peak"),
            rest_seconds=set_data.get("rest_seconds"),
        )

        errors = exercise_set.validate()
        if errors:
            raise ValueError(f"Invalid set data: {'; '.join(errors)}")

        self._set_repo.save(exercise_set)

        event_payload = {
            "set_id": exercise_set.id,
            "session_id": session_id,
            "exercise_id": exercise_set.exercise_id,
            "load_kg": exercise_set.load_kg,
            "reps": exercise_set.reps,
            "rir_reported": exercise_set.rir_reported,
            "rpe_reported": exercise_set.rpe_reported,
            "bpm_avg": exercise_set.bpm_avg,
            "bpm_peak": exercise_set.bpm_peak,
        }
        event = SetRecorded(set_data=event_payload)
        self._publisher.publish("set.recorded", event.to_json())
        return exercise_set


class GetSessionUseCase:
    def __init__(self, session_repo: SessionRepository) -> None:
        self._session_repo = session_repo

    def execute(self, session_id: str) -> WorkoutSession | None:
        return self._session_repo.find_by_id(session_id)
