from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Callable

from fastapi import Depends, Header

from app.core.errors import forbidden, unauthorized
from app.core.security import Role, try_decode_token


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    role: Role
    restaurant_id: str


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    payload = try_decode_token(token)
    if not payload:
        raise unauthorized("Invalid token")

    role = payload.get("role")
    if role not in ("admin", "waiter", "kitchen", "counter"):
        raise unauthorized("Invalid role")

    restaurant_id = payload.get("restaurantId")
    user_id = payload.get("sub")
    if not restaurant_id or not user_id:
        raise unauthorized("Invalid token claims")

    return CurrentUser(user_id=str(user_id), role=role, restaurant_id=str(restaurant_id))


def require_roles(*roles: Role) -> Callable[[CurrentUser], CurrentUser]:
    async def dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if user.role not in roles:
            raise forbidden("Insufficient role")
        return user

    return dep

