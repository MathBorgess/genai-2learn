"""Worker: RabbitMQ consumer that processes workout events."""
from __future__ import annotations

import json
import logging
import signal
import sys
import time
from typing import Any

import pika
import pika.exceptions

from config import Config
from handlers.set_recorded import SetRecordedHandler
from handlers.dlq_handler import DLQHandler
from pipeline.orchestrator import PipelineOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "worker", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()
        self._connection: pika.BlockingConnection | None = None
        self._channel = None
        self._running = False

        orchestrator = PipelineOrchestrator(self._config.EFFORT_INTELLIGENCE_URL)
        self._set_recorded_handler = SetRecordedHandler(orchestrator)
        self._dlq_handler = DLQHandler()

    def _connect(self) -> None:
        params = pika.URLParameters(self._config.RABBITMQ_URL)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

        self._channel.exchange_declare(
            exchange=self._config.EXCHANGE_NAME,
            exchange_type="topic",
            durable=True,
        )

        self._channel.queue_declare(
            queue=self._config.SET_RECORDED_QUEUE,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": self._config.DLQ_QUEUE,
            },
        )
        self._channel.queue_bind(
            exchange=self._config.EXCHANGE_NAME,
            queue=self._config.SET_RECORDED_QUEUE,
            routing_key="set.recorded",
        )

        self._channel.queue_declare(
            queue=self._config.DLQ_QUEUE,
            durable=True,
        )

        self._channel.basic_qos(prefetch_count=self._config.PREFETCH_COUNT)
        logger.info("Connected to RabbitMQ and queues declared")

    def _on_set_recorded(self, channel, method, properties, body: bytes) -> None:
        try:
            event = json.loads(body.decode("utf-8"))
            self._set_recorded_handler.handle(event)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in set.recorded message: %s", exc)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as exc:
            logger.error("Error processing set.recorded message: %s", exc)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _on_dlq_message(self, channel, method, properties, body: bytes) -> None:
        headers = properties.headers if properties else None
        self._dlq_handler.handle(body, headers)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start(self) -> None:
        self._running = True

        def _shutdown(signum, frame):
            logger.info("Shutdown signal received")
            self._running = False
            if self._connection and self._connection.is_open:
                self._connection.close()
            sys.exit(0)

        signal.signal(signal.SIGTERM, _shutdown)
        signal.signal(signal.SIGINT, _shutdown)

        retry_delay = 5
        while self._running:
            try:
                logger.info("Connecting to RabbitMQ...")
                self._connect()

                self._channel.basic_consume(
                    queue=self._config.SET_RECORDED_QUEUE,
                    on_message_callback=self._on_set_recorded,
                )
                self._channel.basic_consume(
                    queue=self._config.DLQ_QUEUE,
                    on_message_callback=self._on_dlq_message,
                )

                logger.info("Worker started. Consuming from %s and %s",
                            self._config.SET_RECORDED_QUEUE,
                            self._config.DLQ_QUEUE)
                self._channel.start_consuming()

            except pika.exceptions.AMQPConnectionError as exc:
                logger.error("RabbitMQ connection failed: %s. Retrying in %ds", exc, retry_delay)
                time.sleep(retry_delay)
            except KeyboardInterrupt:
                logger.info("Worker stopped by user")
                break


if __name__ == "__main__":
    worker = Worker()
    worker.start()
