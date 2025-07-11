from enum import Enum


class HttpStatus(Enum):
    OK = (200, "Success")
    CREATED = (201, "Created")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    CONFLICT = (409, "Conflict")
    SERVER_ERROR = (500, "Internal Server Error")

    def __init__(self, code, message):
        self.code = code
        self.message = message
