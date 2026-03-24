import os
import logging
from flask import Flask
from flask_cors import CORS

from config import Config
from routes.health import health_bp
from routes.estimates import estimates_bp
from routes.recommendations import recommendations_bp


def create_app(
    config: type = Config,
    estimate_repo=None,
    recommendation_repo=None,
    publisher=None,
) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    logging.basicConfig(
        level=logging.INFO,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "service": "effort-intelligence", "message": "%(message)s"}',
    )

    CORS(app)

    if estimate_repo is None:
        from infrastructure.repositories import PostgresEstimateRepository
        estimate_repo = PostgresEstimateRepository()
    if recommendation_repo is None:
        from infrastructure.repositories import PostgresRecommendationRepository
        recommendation_repo = PostgresRecommendationRepository()
    if publisher is None:
        from infrastructure.publisher import RabbitMQPublisher
        publisher = RabbitMQPublisher(
            rabbitmq_url=app.config["RABBITMQ_URL"],
            exchange_name=app.config["EXCHANGE_NAME"],
        )

    app.config["ESTIMATE_REPO"] = estimate_repo
    app.config["RECOMMENDATION_REPO"] = recommendation_repo
    app.config["EVENT_PUBLISHER"] = publisher

    app.register_blueprint(health_bp)
    app.register_blueprint(estimates_bp)
    app.register_blueprint(recommendations_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=8002, debug=os.environ.get("FLASK_ENV") == "development")
