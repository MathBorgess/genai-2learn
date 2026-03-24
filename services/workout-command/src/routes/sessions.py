from flask import Blueprint, jsonify, request, current_app
from application.use_cases import StartSessionUseCase, GetSessionUseCase
from diplomat.adapters import session_from_request, session_to_response

sessions_bp = Blueprint("sessions", __name__)


def _get_use_cases():
    session_repo = current_app.config["SESSION_REPO"]
    publisher = current_app.config["EVENT_PUBLISHER"]
    return (
        StartSessionUseCase(session_repo, publisher),
        GetSessionUseCase(session_repo),
    )


@sessions_bp.route("/sessions", methods=["POST"])
def create_session():
    data = request.get_json(silent=True) or {}

    if not data.get("athlete_id"):
        return jsonify({"error": "athlete_id is required"}), 400

    start_uc, _ = _get_use_cases()
    params = session_from_request(data)

    try:
        session = start_uc.execute(**params)
        return jsonify(session_to_response(session)), 201
    except Exception as exc:
        current_app.logger.error("Failed to create session: %s", exc)
        return jsonify({"error": str(exc)}), 500


@sessions_bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    _, get_uc = _get_use_cases()
    session = get_uc.execute(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session_to_response(session)), 200
