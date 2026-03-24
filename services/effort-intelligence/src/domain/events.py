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
class EffortEstimated(DomainEvent):
    def __init__(self, estimate_data: dict, **kwargs: Any) -> None:
        super().__init__(
            event_type="effort.estimated",
            payload=estimate_data,
            **kwargs,
        )


@dataclass
class RecommendationIssued(DomainEvent):
    def __init__(self, recommendation_data: dict, **kwargs: Any) -> None:
        super().__init__(
            event_type="recommendation.issued",
            payload=recommendation_data,
            **kwargs,
        )
