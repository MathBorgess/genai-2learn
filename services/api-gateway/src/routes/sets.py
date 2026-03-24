import requests
from flask import Blueprint, jsonify, request, current_app
from middleware.auth import require_auth

sets_bp = Blueprint("sets", __name__)


def _workout_command_url() -> str:
    return current_app.config["WORKOUT_COMMAND_URL"]


def _effort_intelligence_url() -> str:
    return current_app.config["EFFORT_INTELLIGENCE_URL"]


@sets_bp.route("/api/v1/sessions/<session_id>/sets", methods=["POST"])
@require_auth
def record_set(session_id: str):
    try:
        resp = requests.post(
            f"{_workout_command_url()}/sessions/{session_id}/sets",
            json=request.get_json(),
            timeout=10,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException as exc:
        current_app.logger.error("workout-command unreachable: %s", exc)
        return jsonify({"error": "upstream service unavailable"}), 502


@sets_bp.route("/api/v1/recommendations/<set_id>", methods=["GET"])
@require_auth
def get_recommendation(set_id: str):
    try:
        resp = requests.get(
            f"{_effort_intelligence_url()}/recommendations/{set_id}",
            timeout=10,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException as exc:
        current_app.logger.error("effort-intelligence unreachable: %s", exc)
        return jsonify({"error": "upstream service unavailable"}), 502


@sets_bp.route("/api/v1/estimates/<set_id>", methods=["GET"])
@require_auth
def get_estimate(set_id: str):
    try:
        resp = requests.get(
            f"{_effort_intelligence_url()}/estimates/{set_id}",
            timeout=10,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException as exc:
        current_app.logger.error("effort-intelligence unreachable: %s", exc)
        return jsonify({"error": "upstream service unavailable"}), 502
