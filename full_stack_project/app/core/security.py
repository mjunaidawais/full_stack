from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Role = Literal["admin", "waiter", "kitchen", "counter"]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _encode(payload: dict[str, Any], ttl_seconds: int, token_type: str) -> str:
    exp = _now() + timedelta(seconds=ttl_seconds)
    to_encode = dict(payload)
    to_encode.update(
        {
            "iss": settings.jwt_issuer,
            "iat": int(_now().timestamp()),
            "exp": int(exp.timestamp()),
            "typ": token_type,
        }
    )
    return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")


def create_token_pair(*, user_id: str, role: Role, restaurant_id: str) -> TokenPair:
    base = {"sub": user_id, "role": role, "restaurantId": restaurant_id}
    return TokenPair(
        access_token=_encode(base, settings.jwt_access_ttl_seconds, "access"),
        refresh_token=_encode(base, settings.jwt_refresh_ttl_seconds, "refresh"),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer)


def try_decode_token(token: str) -> dict[str, Any] | None:
    try:
        return decode_token(token)
    except JWTError:
        return None

