from flask import Blueprint, request, jsonify
from app.models import User
from app.utils.jwt import verify_token
from app.enum.http_status import HttpStatus
from app.utils.response import make_response
from app.utils.serializer import serialize

bp = Blueprint("user", __name__)


def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    payload = verify_token(token, expected_type="access")

    if not payload:
        return None

    return User.query.get(payload["user_id"])


@bp.route("/me", methods=["GET"])
def get_me():
    user = get_current_user()
    if not user:
        return make_response(HttpStatus.UNAUTHORIZED, message="Unauthorized")

    return make_response(HttpStatus.OK, serialize(user, exclude_fields=["password_hash"], include_relationships=True))


@bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "username": u.username} for u in users
    ])
