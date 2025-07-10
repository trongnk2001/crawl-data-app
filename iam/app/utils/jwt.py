import jwt
from datetime import datetime, timedelta
from config import Config


def create_access_token(data, expires_delta=timedelta(minutes=15)):
    data = data.copy()
    data["exp"] = datetime.utcnow() + expires_delta
    data["type"] = "access"
    return jwt.encode(data, Config.JWT_SECRET, algorithm="HS256")


def create_refresh_token(data, expires_delta=timedelta(days=7)):
    data = data.copy()
    data["exp"] = datetime.utcnow() + expires_delta
    data["type"] = "refresh"
    return jwt.encode(data, Config.JWT_SECRET, algorithm="HS256")


def verify_token(token, expected_type=None):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        if expected_type and payload.get("type") != expected_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
