"""Handler for Dead Letter Queue messages."""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class DLQHandler:
    """Logs and records dead-lettered messages for investigation."""

    def handle(self, raw_body: bytes, headers: dict[str, Any] | None = None) -> None:
        try:
            message = json.loads(raw_body.decode("utf-8"))
            event_type = message.get("event_type", "unknown")
            correlation_id = message.get("correlation_id", "unknown")
            
            logger.error(
                "DLQ message received: event_type=%s correlation_id=%s",
                event_type,
                correlation_id,
            )
            logger.error("DLQ message payload: %s", json.dumps(message, indent=2))
            
            if headers:
                death_info = headers.get("x-death", [])
                for death in death_info:
                    logger.error(
                        "Death info: queue=%s reason=%s count=%s",
                        death.get("queue"),
                        death.get("reason"),
                        death.get("count"),
                    )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.error(
                "DLQ: Could not parse message body: %s. Raw: %s",
                exc,
                raw_body[:200],
            )
