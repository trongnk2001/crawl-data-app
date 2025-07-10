from flask import Blueprint, request, jsonify
from app.models import Role, Permission
from app.database import db

bp = Blueprint("role", __name__, url_prefix="/roles")


@bp.route("", methods=["GET"])
def get_roles():
    roles = Role.query.all()
    return jsonify([{"id": r.id, "name": r.name} for r in roles])


@bp.route("", methods=["POST"])
def create_role():
    name = request.json.get("name")
    if Role.query.filter_by(name=name).first():
        return jsonify({"error": "Role exists"}), 409
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    return jsonify({"message": "Role created", "id": role.id})


@bp.route("/<int:role_id>/assign-permission", methods=["POST"])
def assign_permission(role_id):
    permission_name = request.json.get("permission")
    role = Role.query.get(role_id)
    permission = Permission.query.filter_by(name=permission_name).first()
    if not role or not permission:
        return jsonify({"error": "Role or permission not found"}), 404
    role.permissions.append(permission)
    db.session.commit()
    return jsonify({"message": "Permission assigned"})
