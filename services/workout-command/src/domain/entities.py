from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class WorkoutSession:
    athlete_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"
    planned_workout: Optional[dict] = None
    readiness_score: Optional[float] = None

    def complete(self) -> None:
        self.status = "completed"

    def cancel(self) -> None:
        self.status = "cancelled"


@dataclass
class ExerciseSet:
    session_id: str
    exercise_id: str
    load_kg: float
    reps: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rir_reported: Optional[float] = None
    rpe_reported: Optional[float] = None
    bpm_avg: Optional[float] = None
    bpm_peak: Optional[float] = None
    rest_seconds: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.load_kg < 0 or self.load_kg > 500:
            errors.append("load_kg must be between 0 and 500")
        if self.reps < 1 or self.reps > 50:
            errors.append("reps must be between 1 and 50")
        if self.bpm_avg is not None and (self.bpm_avg < 40 or self.bpm_avg > 220):
            errors.append("bpm_avg must be between 40 and 220")
        return errors
