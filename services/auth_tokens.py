import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

ALGORITHM = "HS256"
TOKEN_LIFETIME_MINUTES = 30


def create_access_token(user_id: int) -> str:
    secret = os.getenv("JWT_SECRET_KEY")

    if not secret or len(secret) < 64:
        raise RuntimeError("JWT_SECRET_KEY must be a 64-character secret")

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_LIFETIME_MINUTES
    )

    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        secret,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int | None:
    secret = os.getenv("JWT_SECRET_KEY")

    if not secret or len(secret) < 64:
        raise RuntimeError("JWT_SECRET_KEY must be a 64-character secret")

    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        user_id = int(claims["sub"])
        return user_id if user_id > 0 else None
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None