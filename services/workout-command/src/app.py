import logging
from flask import Flask
from flask_cors import CORS

from config import Config
from routes.health import health_bp
from routes.sessions import sessions_bp
from routes.sets import sets_bp


def create_app(config: type = Config, session_repo=None, set_repo=None, publisher=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    logging.basicConfig(
        level=logging.INFO,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "workout-command", "message": "%(message)s"}',
    )

    CORS(app)

    # Wire dependencies (allow injection for testing)
    if session_repo is None:
        from infrastructure.repositories import PostgresSessionRepository
        session_repo = PostgresSessionRepository()
    if set_repo is None:
        from infrastructure.repositories import PostgresSetRepository
        set_repo = PostgresSetRepository()
    if publisher is None:
        from infrastructure.publisher import RabbitMQPublisher
        publisher = RabbitMQPublisher(
            rabbitmq_url=app.config["RABBITMQ_URL"],
            exchange_name=app.config["EXCHANGE_NAME"],
        )

    app.config["SESSION_REPO"] = session_repo
    app.config["SET_REPO"] = set_repo
    app.config["EVENT_PUBLISHER"] = publisher

    app.register_blueprint(health_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(sets_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=8001, debug=True)
