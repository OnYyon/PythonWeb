from flask import Blueprint, jsonify, request
from .service import get_recommendations

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/recommendations", methods=["GET"], strict_slashes=False)
def recommendations():
    user_id = request.headers.get("X-User-Id")

    if not user_id:
        return jsonify({"error": "X-User-Id header is required"}), 400

    result = get_recommendations(user_id)

    return jsonify(result), 200
