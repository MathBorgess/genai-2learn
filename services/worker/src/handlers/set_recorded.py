"""Handler for set.recorded events."""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class SetRecordedHandler:
    """Processes set.recorded events by invoking the agent pipeline."""

    def __init__(self, orchestrator) -> None:
        self._orchestrator = orchestrator

    def handle(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = event.get("payload", {})
        correlation_id = event.get("correlation_id", "")
        
        logger.info(
            "Processing set.recorded event: set_id=%s correlation_id=%s",
            payload.get("set_id"),
            correlation_id,
        )

        set_data = {**payload, "correlation_id": correlation_id}
        result = self._orchestrator.process(set_data)

        logger.info(
            "Completed pipeline for set_id=%s action=%s",
            payload.get("set_id"),
            result.get("recommendation", {}).get("action_type"),
        )
        return result
