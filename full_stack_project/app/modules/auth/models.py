from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Role = Literal["admin", "waiter", "kitchen", "counter"]


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    restaurantId: str = Field(min_length=1)


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str


class UserPublic(BaseModel):
    id: str
    name: str
    role: Role
    restaurantId: str

