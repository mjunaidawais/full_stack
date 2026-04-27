from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.errors import unauthorized
from app.middlewares.rbac import CurrentUser, get_current_user
from app.modules.auth.models import LoginRequest, TokenResponse, UserPublic
from app.modules.auth.service import ensure_seed_admin, get_user_public, login


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login_route(body: LoginRequest) -> TokenResponse:
    # Scaffold convenience: ensure an admin exists per restaurant.
    await ensure_seed_admin(restaurant_id=body.restaurantId)
    access, refresh = await login(
        username=body.username, password=body.password, restaurant_id=body.restaurantId
    )
    if not access:
        raise unauthorized("Invalid credentials")
    return TokenResponse(accessToken=access, refreshToken=refresh)


@router.get("/me", response_model=UserPublic)
async def me_route(user: CurrentUser = Depends(get_current_user)) -> UserPublic:
    pub = await get_user_public(user.user_id)
    return UserPublic(**pub)

