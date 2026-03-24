import requests
from flask import Blueprint, jsonify, request, current_app
from middleware.auth import require_auth

sessions_bp = Blueprint("sessions", __name__)


def _workout_command_url() -> str:
    return current_app.config["WORKOUT_COMMAND_URL"]


@sessions_bp.route("/api/v1/sessions", methods=["POST"])
@require_auth
def create_session():
    try:
        resp = requests.post(
            f"{_workout_command_url()}/sessions",
            json=request.get_json(),
            timeout=10,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException as exc:
        current_app.logger.error("workout-command unreachable: %s", exc)
        return jsonify({"error": "upstream service unavailable"}), 502


@sessions_bp.route("/api/v1/sessions/<session_id>", methods=["GET"])
@require_auth
def get_session(session_id: str):
    try:
        resp = requests.get(
            f"{_workout_command_url()}/sessions/{session_id}",
            timeout=10,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException as exc:
        current_app.logger.error("workout-command unreachable: %s", exc)
        return jsonify({"error": "upstream service unavailable"}), 502
