import os

class Config:
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-prod")
    WORKOUT_COMMAND_URL: str = os.getenv("WORKOUT_COMMAND_URL", "http://localhost:8001")
    EFFORT_INTELLIGENCE_URL: str = os.getenv("EFFORT_INTELLIGENCE_URL", "http://localhost:8002")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    RATELIMIT_DEFAULT: str = os.getenv("RATELIMIT_DEFAULT", "100 per minute")
    RATELIMIT_STORAGE_URI: str = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
