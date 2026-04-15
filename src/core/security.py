import datetime as dt
import logging
import uuid

import jwt
import redis.asyncio as redis
from fastapi import HTTPException, status
from passlib.hash import argon2

from src.core.config import settings

logger = logging.getLogger(__name__)

# ── Key loading ──────────────────────────────────────────

_private_key: str | None = None
_public_key: str | None = None


def load_keys() -> None:
    global _private_key, _public_key
    with open(settings.JWT_PRIVATE_KEY_PATH) as f:
        _private_key = f.read()
    with open(settings.JWT_PUBLIC_KEY_PATH) as f:
        _public_key = f.read()


# ── Password hashing (Argon2) ───────────────────────────


def hash_password(password: str) -> str:
    return argon2.using(
        memory_cost=131072,
        time_cost=3,
        parallelism=4,
        salt_len=64,
        digest_size=64,
    ).hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return argon2.verify(password, hashed)


# ── JWT tokens ──────────────────────────────────────────


def create_access_token(user_id: int) -> str:
    now = dt.datetime.now(dt.UTC)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + dt.timedelta(seconds=settings.ACCESS_TOKEN_LIFETIME),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, _private_key, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    now = dt.datetime.now(dt.UTC)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + dt.timedelta(seconds=settings.REFRESH_TOKEN_LIFETIME),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, _private_key, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    """Decode access token and return user_id. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, _public_key, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from e

    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    return int(payload["sub"])


async def decode_refresh_token(token: str, redis_client: redis.Redis) -> int:
    """Decode refresh token, verify it exists in Redis, and revoke it (single-use)."""
    try:
        payload = jwt.decode(token, _public_key, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token") from e

    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    user_id = int(payload["sub"])
    jti = payload["jti"]

    # Check and revoke (single-use)
    key = f"user:{user_id}:refresh:{jti}"
    exists = await redis_client.delete(key)
    if not exists:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token revoked or not found")

    return user_id


async def store_refresh_token(user_id: int, token: str, redis_client: redis.Redis) -> None:
    """Store refresh token JTI in Redis with TTL."""
    payload = jwt.decode(token, _public_key, algorithms=[settings.JWT_ALGORITHM])
    jti = payload["jti"]
    key = f"user:{user_id}:refresh:{jti}"
    await redis_client.setex(key, settings.REFRESH_TOKEN_LIFETIME, "1")
