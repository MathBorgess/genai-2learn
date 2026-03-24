import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import jwt
import time
from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    JWT_SECRET_KEY = "test-secret"
    WORKOUT_COMMAND_URL = "http://mock-workout-command:8001"
    EFFORT_INTELLIGENCE_URL = "http://mock-effort-intelligence:8002"
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URI = "memory://"


@pytest.fixture
def app():
    application = create_app(TestConfig)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    token = jwt.encode(
        {"sub": "athlete-123", "exp": int(time.time()) + 3600},
        "test-secret",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}
