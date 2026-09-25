from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings
from app.utils.exceptions import AuthenticationException

ALGORITHM = "HS256"


def create_token(data: dict, expires_delta: timedelta) -> str:
    """Generates a signed JWT token with custom claims and expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decodes a JWT token, verifying its signature and expiration claims."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Credentials expired: access token has expired.")
    except jwt.InvalidTokenError:
        raise AuthenticationException("Authentication failed: invalid token credentials.")
