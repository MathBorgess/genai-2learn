from __future__ import annotations

import json
from typing import Optional
from domain.entities import EffortEstimate, Recommendation
from infrastructure.database import get_db_session
from sqlalchemy import text


class PostgresEstimateRepository:
    def save(self, estimate: EffortEstimate) -> None:
        db = get_db_session()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO effort_estimates (id, set_id, effort_score, rir_estimate, confidence, feature_contributions, created_at)
                    VALUES (:id, :set_id, :effort_score, :rir_estimate, :confidence, :feature_contributions::jsonb, :created_at)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": estimate.id,
                    "set_id": estimate.set_id,
                    "effort_score": estimate.effort_score,
                    "rir_estimate": estimate.rir_estimate,
                    "confidence": estimate.confidence,
                    "feature_contributions": json.dumps(estimate.feature_contributions or {}),
                    "created_at": estimate.created_at,
                },
            )
            db.commit()
        finally:
            db.close()

    def find_by_set_id(self, set_id: str) -> Optional[EffortEstimate]:
        db = get_db_session()
        try:
            row = db.execute(
                text(
                    "SELECT id, set_id, effort_score, rir_estimate, confidence, feature_contributions, created_at "
                    "FROM effort_estimates WHERE set_id = :set_id ORDER BY created_at DESC LIMIT 1"
                ),
                {"set_id": set_id},
            ).fetchone()
            if row is None:
                return None
            return EffortEstimate(
                id=str(row.id),
                set_id=str(row.set_id),
                effort_score=row.effort_score,
                rir_estimate=row.rir_estimate,
                confidence=row.confidence,
                feature_contributions=row.feature_contributions,
                created_at=row.created_at,
            )
        finally:
            db.close()


class PostgresRecommendationRepository:
    def save(self, recommendation: Recommendation) -> None:
        db = get_db_session()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO recommendations (id, set_id, action_type, load_delta_pct, cue_list, safety_reason_codes, rationale, created_at)
                    VALUES (:id, :set_id, :action_type, :load_delta_pct, :cue_list::jsonb, :safety_reason_codes::jsonb, :rationale, :created_at)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": recommendation.id,
                    "set_id": recommendation.set_id,
                    "action_type": recommendation.action_type,
                    "load_delta_pct": recommendation.load_delta_pct,
                    "cue_list": json.dumps(recommendation.cue_list),
                    "safety_reason_codes": json.dumps(recommendation.safety_reason_codes),
                    "rationale": recommendation.rationale,
                    "created_at": recommendation.created_at,
                },
            )
            db.commit()
        finally:
            db.close()

    def find_by_set_id(self, set_id: str) -> Optional[Recommendation]:
        db = get_db_session()
        try:
            row = db.execute(
                text(
                    "SELECT id, set_id, action_type, load_delta_pct, cue_list, safety_reason_codes, rationale, created_at "
                    "FROM recommendations WHERE set_id = :set_id ORDER BY created_at DESC LIMIT 1"
                ),
                {"set_id": set_id},
            ).fetchone()
            if row is None:
                return None
            return Recommendation(
                id=str(row.id),
                set_id=str(row.set_id),
                action_type=row.action_type,
                load_delta_pct=row.load_delta_pct,
                rationale=row.rationale,
                cue_list=row.cue_list if isinstance(row.cue_list, list) else [],
                safety_reason_codes=row.safety_reason_codes if isinstance(row.safety_reason_codes, list) else [],
                created_at=row.created_at,
            )
        finally:
            db.close()
