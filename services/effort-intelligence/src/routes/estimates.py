from flask import Blueprint, jsonify, current_app
from application.use_cases import GetEstimateUseCase
from diplomat.adapters import estimate_to_response

estimates_bp = Blueprint("estimates", __name__)


@estimates_bp.route("/estimates/<set_id>", methods=["GET"])
def get_estimate(set_id: str):
    estimate_repo = current_app.config["ESTIMATE_REPO"]
    use_case = GetEstimateUseCase(estimate_repo)
    estimate = use_case.execute(set_id)
    if estimate is None:
        return jsonify({"error": "Estimate not found", "set_id": set_id}), 404
    return jsonify(estimate_to_response(estimate)), 200
