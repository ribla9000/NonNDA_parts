from passlib.context import CryptContext
import jwt
from core.config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ACCESS_SECRET_KEY
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    to_encode = {**data}
    encoded = jwt.encode(payload=to_encode, key=ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def decode_access_token(token):
    try:
        encoded_jwt = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=ALGORITHM)
    except jwt.PyJWTError:
        return False
    return encoded_jwt


