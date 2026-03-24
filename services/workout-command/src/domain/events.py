from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
import uuid
import json


@dataclass
class DomainEvent:
    event_type: str
    payload: dict
    version: str = "1"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self) -> str:
        return json.dumps(asdict(self))


@dataclass
class SessionStarted(DomainEvent):
    event_type: str = field(default="session.started", init=False)

    def __init__(self, session_id: str, athlete_id: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="session.started",
            payload={"session_id": session_id, "athlete_id": athlete_id},
            **kwargs,
        )


@dataclass
class SetRecorded(DomainEvent):
    event_type: str = field(default="set.recorded", init=False)

    def __init__(self, set_data: dict, **kwargs: Any) -> None:
        super().__init__(
            event_type="set.recorded",
            payload=set_data,
            **kwargs,
        )
