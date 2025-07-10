from flask import Blueprint, request, jsonify
from app.models import User
from app.utils.jwt import verify_token

bp = Blueprint("user", __name__)


def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    payload = verify_token(token, expected_type="access")
    return User.query.get(payload["user_id"]) if payload else None


@bp.route("/me", methods=["GET"])
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "id": user.id,
        "username": user.username,
        "roles": [r.name for r in user.roles]
    })


@bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "username": u.username} for u in users
    ])
