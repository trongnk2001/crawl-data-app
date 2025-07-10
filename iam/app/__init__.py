
from flask import Flask
from config import Config
from flasgger import Swagger
from app.database import db, migrate
from .routes import user, role, permission, auth
from flask import Blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    root_bp = Blueprint("auth_root", __name__, url_prefix="/auth")
    root_bp.register_blueprint(auth.bp)
    root_bp.register_blueprint(user.bp)
    root_bp.register_blueprint(role.bp)
    root_bp.register_blueprint(permission.bp)
    app.register_blueprint(root_bp)

    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "IAM API",
            "description": "API quản lý xác thực & phân quyền",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header. Example: 'Bearer {token}'"
            }
        }
    })

    return app
