from flask import Blueprint, jsonify, current_app
from application.use_cases import GetRecommendationUseCase
from diplomat.adapters import recommendation_to_response

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/recommendations/<set_id>", methods=["GET"])
def get_recommendation(set_id: str):
    recommendation_repo = current_app.config["RECOMMENDATION_REPO"]
    use_case = GetRecommendationUseCase(recommendation_repo)
    recommendation = use_case.execute(set_id)
    if recommendation is None:
        return jsonify({"error": "Recommendation not found", "set_id": set_id}), 404
    return jsonify(recommendation_to_response(recommendation)), 200
