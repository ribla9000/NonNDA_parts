class ResponseException(Exception):
    def __init__(self, error):
        self.error = error


def response_error(error: dict):
    return response_wrapper(
        error={
            "code": error.get("code"),
            "message": error.get("message")
        },
        status=False,
        payload=None)


def response_success(payload):
    return response_wrapper(payload=payload)


def response_wrapper(payload=None, status=True, error=None):
    return {"error": error,
            "payload": payload,
            "status": status}
