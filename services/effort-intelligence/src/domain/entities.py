from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class EffortEstimate:
    set_id: str
    effort_score: float
    rir_estimate: float
    confidence: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature_contributions: Optional[dict] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Recommendation:
    set_id: str
    action_type: str
    load_delta_pct: float
    rationale: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cue_list: list = field(default_factory=list)
    safety_reason_codes: list = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
