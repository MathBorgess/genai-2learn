import os


class Config:
    RABBITMQ_URL: str = os.getenv(
        "RABBITMQ_URL",
        "amqp://genai:genai_secret@localhost:5672/",
    )
    EFFORT_INTELLIGENCE_URL: str = os.getenv(
        "EFFORT_INTELLIGENCE_URL",
        "http://localhost:8002",
    )
    EXCHANGE_NAME: str = "genai2learn"
    SET_RECORDED_QUEUE: str = "set.recorded"
    DLQ_QUEUE: str = "set.recorded.dlq"
    PREFETCH_COUNT: int = int(os.getenv("PREFETCH_COUNT", "1"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
