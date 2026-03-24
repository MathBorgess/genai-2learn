import logging
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from routes.health import health_bp
from routes.sessions import sessions_bp
from routes.sets import sets_bp


def create_app(config: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    # Structured logging
    logging.basicConfig(
        level=logging.INFO,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "api-gateway", "message": "%(message)s"}',
    )

    CORS(app)

    Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config.get("RATELIMIT_DEFAULT", "100 per minute")],
        storage_uri=app.config.get("RATELIMIT_STORAGE_URI", "memory://"),
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(sets_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    debug = application.config.get("FLASK_ENV") == "development"
    application.run(host="0.0.0.0", port=8000, debug=debug)
