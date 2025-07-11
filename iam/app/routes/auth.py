from flask import Blueprint, request, jsonify
from app.models import User, Role
from app.database import db
from app.utils.security import hash_password, check_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_token
from app.enum.http_status import HttpStatus
from app.utils.response import make_response

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return make_response(HttpStatus.BAD_REQUEST, None, "Missing credentials")

    if User.query.filter_by(username=username).first():
        return make_response(HttpStatus.CONFLICT, None, "Username exists")

    user = User(username=username, password_hash=hash_password(password))
    user_role = Role.query.filter_by(name="user").first()
    if not user_role:
        user_role = Role(name="user")
        db.session.add(user_role)
    user.roles.append(user_role)
    db.session.add(user)
    db.session.commit()

    return make_response(HttpStatus.CREATED)


@bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if not user or not check_password(data.get("password"), user.password_hash):
        return make_response(HttpStatus.UNAUTHORIZED, None, "Incorrect username or password")

    token_data = {"user_id": user.id}
    access = create_access_token(token_data)
    refresh = create_refresh_token(token_data)
    return make_response(HttpStatus.OK, {"access_token": access, "refresh_token": refresh})


@bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    data = request.json
    refresh_token = data.get("refresh_token")
    payload = verify_token(refresh_token, expected_type="refresh")
    if not payload:
        return make_response(HttpStatus.UNAUTHORIZED, None, "Invalid refresh token")

    new_token = create_access_token({"user_id": payload["user_id"]})
    return make_response(HttpStatus.OK, {"access_token": new_token})
