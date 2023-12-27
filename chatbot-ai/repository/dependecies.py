from core.config import ENVIRONMENT
from core.http_codes import BadRequests
from repository.security import decode_access_token
from fastapi import Request


async def auth_required(request: Request):

    if ENVIRONMENT == "development":
        return True, {}

    headers = request.headers
    api_token = headers.get("API-TOKEN")

    if api_token is None:
        return False, BadRequests.TOKEN_IS_NONE

    payload = decode_access_token(api_token)

    if not payload:
        return False, BadRequests.INVALID_TOKEN

    return True, payload
