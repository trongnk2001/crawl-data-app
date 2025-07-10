from app.database import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship("Role", secondary="user_roles", backref="users")


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    permissions = db.relationship(
        "Permission", secondary="role_permissions", backref="roles")


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer,
                                db.ForeignKey('user.id')),
                      db.Column('role_id', db.Integer,
                                db.ForeignKey('role.id'))
                      )

role_permissions = db.Table('role_permissions',
                            db.Column('role_id', db.Integer,
                                      db.ForeignKey('role.id')),
                            db.Column('permission_id', db.Integer,
                                      db.ForeignKey('permission.id'))
                            )
