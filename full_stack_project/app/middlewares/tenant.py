from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header

from app.core.errors import bad_request


async def get_restaurant_id(x_restaurant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_restaurant_id:
        raise bad_request("Missing X-Restaurant-Id header")
    return x_restaurant_id

