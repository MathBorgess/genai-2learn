from flask import Blueprint, jsonify, request, current_app
from application.use_cases import RecordSetUseCase
from diplomat.adapters import set_from_request, set_to_response

sets_bp = Blueprint("sets", __name__)


def _get_use_case():
    session_repo = current_app.config["SESSION_REPO"]
    set_repo = current_app.config["SET_REPO"]
    publisher = current_app.config["EVENT_PUBLISHER"]
    return RecordSetUseCase(session_repo, set_repo, publisher)


@sets_bp.route("/sessions/<session_id>/sets", methods=["POST"])
def record_set(session_id: str):
    data = request.get_json(silent=True) or {}

    required_fields = ["exercise_id", "load_kg", "reps"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    use_case = _get_use_case()
    set_data = set_from_request(data)

    try:
        exercise_set = use_case.execute(session_id, set_data)
        return jsonify(set_to_response(exercise_set)), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        current_app.logger.error("Failed to record set: %s", exc)
        return jsonify({"error": str(exc)}), 500
