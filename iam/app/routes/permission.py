from flask import Blueprint, request, jsonify
from app.models import Permission
from app.database import db

bp = Blueprint("permission", __name__, url_prefix="/permissions")


@bp.route("", methods=["GET"])
def get_permissions():
    permissions = Permission.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in permissions])


@bp.route("", methods=["POST"])
def create_permission():
    name = request.json.get("name")
    if Permission.query.filter_by(name=name).first():
        return jsonify({"error": "Permission exists"}), 409
    perm = Permission(name=name)
    db.session.add(perm)
    db.session.commit()
    return jsonify({"message": "Permission created", "id": perm.id})
