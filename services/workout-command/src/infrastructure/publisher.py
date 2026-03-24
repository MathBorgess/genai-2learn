from __future__ import annotations

import logging
import pika
from flask import Flask

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self, rabbitmq_url: str, exchange_name: str) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._exchange_name = exchange_name

    def _get_channel(self):
        params = pika.URLParameters(self._rabbitmq_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=self._exchange_name,
            exchange_type="topic",
            durable=True,
        )
        return connection, channel

    def publish(self, routing_key: str, event_json: str) -> None:
        connection = None
        try:
            connection, channel = self._get_channel()
            channel.basic_publish(
                exchange=self._exchange_name,
                routing_key=routing_key,
                body=event_json.encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type="application/json",
                ),
            )
            logger.info("Published event to %s: %s", routing_key, event_json)
        except Exception as exc:
            logger.error("Failed to publish event: %s", exc)
            raise
        finally:
            if connection and not connection.is_closed:
                connection.close()


class NoOpPublisher:
    """No-op publisher for testing."""
    def publish(self, routing_key: str, event_json: str) -> None:
        logger.debug("NoOpPublisher: would publish to %s", routing_key)
