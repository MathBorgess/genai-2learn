from __future__ import annotations

from typing import Protocol, Optional
from domain.entities import EffortEstimate, Recommendation
from domain.events import EffortEstimated, RecommendationIssued
from agents.pipeline import AgentPipeline


class EstimateRepository(Protocol):
    def save(self, estimate: EffortEstimate) -> None: ...
    def find_by_set_id(self, set_id: str) -> Optional[EffortEstimate]: ...


class RecommendationRepository(Protocol):
    def save(self, recommendation: Recommendation) -> None: ...
    def find_by_set_id(self, set_id: str) -> Optional[Recommendation]: ...


class EventPublisher(Protocol):
    def publish(self, routing_key: str, event_json: str) -> None: ...


class ProcessSetUseCase:
    """Runs the full agent pipeline for a recorded set."""

    def __init__(
        self,
        estimate_repo: EstimateRepository,
        recommendation_repo: RecommendationRepository,
        publisher: EventPublisher,
        pipeline: Optional[AgentPipeline] = None,
    ) -> None:
        self._estimate_repo = estimate_repo
        self._recommendation_repo = recommendation_repo
        self._publisher = publisher
        self._pipeline = pipeline or AgentPipeline()

    def execute(self, set_data: dict) -> dict:
        result = self._pipeline.run(set_data)

        effort_data = result["effort"]
        estimate = EffortEstimate(
            set_id=set_data.get("set_id", ""),
            effort_score=effort_data["effort_score"],
            rir_estimate=effort_data["rir_estimate"],
            confidence=effort_data["confidence"],
            feature_contributions=effort_data.get("feature_contributions"),
        )
        self._estimate_repo.save(estimate)

        effort_event = EffortEstimated(
            estimate_data={
                "set_id": estimate.set_id,
                "effort_score": estimate.effort_score,
                "rir_estimate": estimate.rir_estimate,
                "confidence": estimate.confidence,
            },
            correlation_id=set_data.get("correlation_id", ""),
        )
        self._publisher.publish("effort.estimated", effort_event.to_json())

        rec_data = result["recommendation"]
        recommendation = Recommendation(
            set_id=set_data.get("set_id", ""),
            action_type=rec_data["action_type"],
            load_delta_pct=rec_data["load_delta_pct"],
            rationale=rec_data["rationale"],
            cue_list=rec_data.get("cue_list", []),
            safety_reason_codes=rec_data.get("safety_reason_codes", []),
        )
        self._recommendation_repo.save(recommendation)

        rec_event = RecommendationIssued(
            recommendation_data={
                "set_id": recommendation.set_id,
                "action_type": recommendation.action_type,
                "load_delta_pct": recommendation.load_delta_pct,
                "rationale": recommendation.rationale,
            },
            correlation_id=set_data.get("correlation_id", ""),
        )
        self._publisher.publish("recommendation.issued", rec_event.to_json())

        return result


class GetEstimateUseCase:
    def __init__(self, estimate_repo: EstimateRepository) -> None:
        self._estimate_repo = estimate_repo

    def execute(self, set_id: str) -> Optional[EffortEstimate]:
        return self._estimate_repo.find_by_set_id(set_id)


class GetRecommendationUseCase:
    def __init__(self, recommendation_repo: RecommendationRepository) -> None:
        self._recommendation_repo = recommendation_repo

    def execute(self, set_id: str) -> Optional[Recommendation]:
        return self._recommendation_repo.find_by_set_id(set_id)
