import os


class Config:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://genai:genai_secret@localhost:5432/genai2learn",
    )
    RABBITMQ_URL: str = os.getenv(
        "RABBITMQ_URL",
        "amqp://genai:genai_secret@localhost:5672/",
    )
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    EXCHANGE_NAME: str = "genai2learn"
