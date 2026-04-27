from __future__ import annotations

from bson import ObjectId

from app.core.security import Role, create_token_pair, hash_password, verify_password
from app.db.mongo import mongo_db


async def ensure_seed_admin(*, restaurant_id: str) -> None:
    users = mongo_db()["users"]
    existing = await users.find_one({"restaurantId": restaurant_id, "role": "admin"})
    if existing:
        return
    await users.insert_one(
        {
            "name": "Admin",
            "username": "admin",
            "role": "admin",
            "restaurantId": restaurant_id,
            "passwordHash": hash_password("admin123"),
        }
    )


async def login(*, username: str, password: str, restaurant_id: str) -> tuple[str, str]:
    users = mongo_db()["users"]
    user = await users.find_one({"restaurantId": restaurant_id, "username": username})
    if not user:
        return "", ""
    if not verify_password(password, user.get("passwordHash", "")):
        return "", ""
    user_id = str(user["_id"])
    role: Role = user["role"]
    tokens = create_token_pair(user_id=user_id, role=role, restaurant_id=restaurant_id)
    return tokens.access_token, tokens.refresh_token


async def get_user_public(user_id: str) -> dict:
    users = mongo_db()["users"]
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {}
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "role": user.get("role", ""),
        "restaurantId": user.get("restaurantId", ""),
    }

