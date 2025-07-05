from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import User, Role
from db import SessionLocal
import bcrypt
from utils.jwt import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    db = SessionLocal()
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role_name = data.get("role", "user")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    role = db.query(Role).filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.add(role)
        db.commit()

    # Hash mật khẩu
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = User(username=username, role=role)
    user.password_hash = hashed_password.decode('utf-8')

    db.add(user)
    try:
        db.commit()
        return jsonify({"message": "User created"}), 201
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "User already exists"}), 409


@auth_bp.route("/login", methods=["POST"])
def login():
    db = SessionLocal()
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = db.query(User).filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token({"id": user.id, "role": user.role.name})
    return jsonify({"access_token": token})

   