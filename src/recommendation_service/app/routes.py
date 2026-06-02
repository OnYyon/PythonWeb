import uuid
from flask import Blueprint, jsonify, request

from src.shared.auth_token import JwtTokenManager, TokenError
from src.shared.utils.logger import get_logger
from .service import get_recommendations

recommendations_bp = Blueprint("recommendations", __name__)
logger = get_logger(__name__)
token_manager = JwtTokenManager()


@recommendations_bp.route("/recommendations", methods=["GET"], strict_slashes=False)
def recommendations():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]

    try:
        payload = token_manager.parse_and_validate(token)
        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 401

        uuid.UUID(str(user_id))
    except TokenError:
        return jsonify({"error": "Invalid or expired token"}), 401
    except ValueError:
        return jsonify({"error": "Invalid User ID format"}), 400

    try:
        result = get_recommendations(str(user_id))
        return jsonify(result), 200
    except Exception:
        logger.error("Failed to fetch recommendations", exc_info=True, user_id=user_id)
        return jsonify({"error": "Internal server error"}), 500
