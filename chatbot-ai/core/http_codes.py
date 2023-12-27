
class BadRequests:

    INVALID_DATA = {"code": "INVALID_DATA", "message": "Invalid data given"}
    TOKEN_IS_NONE = {"code": "TOKEN_REQUIRED", "message": "Token is None"}
    INVALID_TOKEN = {"code": "INVALID_TOKEN", "message": "Token is expired or token isn't valid"}