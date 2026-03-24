"""Orchestrator: calls effort-intelligence service HTTP API to process set data."""
from __future__ import annotations

import json
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Delegates processing to the effort-intelligence service."""

    def __init__(self, effort_intelligence_url: str, timeout: int = 30) -> None:
        self._base_url = effort_intelligence_url.rstrip("/")
        self._timeout = timeout

    def process(self, set_data: dict[str, Any]) -> dict[str, Any]:
        set_id = set_data.get("set_id")
        
        try:
            response = requests.post(
                f"{self._base_url}/internal/pipeline",
                json=set_data,
                timeout=self._timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                logger.warning(
                    "effort-intelligence /internal/pipeline not available, using fallback"
                )
                return self._conservative_fallback(set_data)
            logger.error("HTTP error calling effort-intelligence: %s", exc)
            raise
        except requests.RequestException as exc:
            logger.error("Failed to reach effort-intelligence: %s", exc)
            raise

    def _conservative_fallback(self, set_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "validation": {"data_quality_score": 0.0},
            "effort": {
                "effort_score": 50.0,
                "rir_estimate": 5.0,
                "confidence": 0.1,
                "feature_contributions": {},
            },
            "recommendation": {
                "action_type": "MAINTAIN",
                "load_delta_pct": 0.0,
                "cue_list": [],
                "safety_reason_codes": ["ORCHESTRATOR_FALLBACK"],
                "rationale": "Pipeline unavailable. Maintaining load as a precaution.",
            },
            "correlation_id": set_data.get("correlation_id"),
            "fallback": True,
        }
