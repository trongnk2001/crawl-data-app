# app/utils/response.py
from flask import jsonify
from app.enum.http_status import HttpStatus


def make_response(status: HttpStatus, data=None, message=None):
    return jsonify({
        "success": status.code == 200 and status.code == 201,
        "code": status.code,
        "message": message or status.message,
        "data": data
    }), status.code
