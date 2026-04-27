from __future__ import annotations

import time

from bson import ObjectId
from pymongo import ReturnDocument

from app.core.errors import bad_request, not_found
from app.db.mongo import mongo_db
from app.events.bus import envelope, publish_event
from app.middlewares.rbac import CurrentUser


def _ts() -> int:
    return int(time.time())


async def create_order(*, restaurant_id: str, user: CurrentUser, body: dict) -> dict:
    orders = mongo_db()["orders"]

    idem_key = body["idempotencyKey"]
    existing = await orders.find_one({"restaurantId": restaurant_id, "idempotencyKey": idem_key})
    if existing:
        return _to_out(existing)

    now = _ts()
    doc = {
        "restaurantId": restaurant_id,
        "tableNumber": body["tableNumber"],
        "items": body["items"],
        "status": "PLACED",
        "createdBy": user.user_id,
        "idempotencyKey": idem_key,
        "createdAt": now,
        "updatedAt": now,
    }
    res = await orders.insert_one(doc)
    doc["_id"] = res.inserted_id

    await publish_event(
        envelope(
            name="OrderCreated",
            restaurant_id=restaurant_id,
            payload={"orderId": str(doc["_id"]), "createdBy": user.user_id},
        )
    )
    return _to_out(doc)


async def list_orders(*, restaurant_id: str, status: str | None = None) -> list[dict]:
    orders = mongo_db()["orders"]
    q: dict = {"restaurantId": restaurant_id}
    if status:
        q["status"] = status
    cursor = orders.find(q).sort("createdAt", -1).limit(200)
    return [_to_out(x) async for x in cursor]


async def update_status(*, restaurant_id: str, order_id: str, status: str, user: CurrentUser) -> dict:
    if status not in ("PLACED", "PREPARING", "READY", "COMPLETED", "CANCELLED"):
        raise bad_request("Invalid status")
    orders = mongo_db()["orders"]
    now = _ts()
    doc = await orders.find_one_and_update(
        {"_id": ObjectId(order_id), "restaurantId": restaurant_id},
        {"$set": {"status": status, "updatedAt": now}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        raise not_found("Order not found")

    await publish_event(
        envelope(
            name="OrderUpdated",
            restaurant_id=restaurant_id,
            payload={"orderId": order_id, "status": status, "updatedBy": user.user_id},
        )
    )
    return _to_out(doc)


def _to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "restaurantId": doc["restaurantId"],
        "tableNumber": doc["tableNumber"],
        "items": doc.get("items", []),
        "status": doc.get("status", "PLACED"),
        "createdBy": doc.get("createdBy", ""),
        "createdAt": int(doc.get("createdAt", 0)),
        "updatedAt": int(doc.get("updatedAt", 0)),
    }

