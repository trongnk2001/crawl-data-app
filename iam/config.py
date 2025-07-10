import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", "postgresql://postgres:admin@localhost:5432/iam")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "dummy-secret")
