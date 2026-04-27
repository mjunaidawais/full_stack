from __future__ import annotations

import time

from bson import ObjectId

from app.core.errors import bad_request, not_found
from app.db.mongo import mongo_db
from app.events.bus import envelope, publish_event


def _ts() -> int:
    return int(time.time())


async def create_payment(*, restaurant_id: str, order_id: str, method: str, amount: float) -> dict:
    orders = mongo_db()["orders"]
    payments = mongo_db()["payments"]

    order = await orders.find_one({"_id": ObjectId(order_id), "restaurantId": restaurant_id})
    if not order:
        raise not_found("Order not found")
    if order.get("status") == "CANCELLED":
        raise bad_request("Cannot pay cancelled order")

    now = _ts()
    doc = {
        "restaurantId": restaurant_id,
        "orderId": order_id,
        "method": method,
        "amount": amount,
        "status": "SUCCESS",
        "createdAt": now,
    }
    res = await payments.insert_one(doc)
    doc["_id"] = res.inserted_id

    # Mark order completed on successful payment (scaffold behavior).
    await orders.update_one(
        {"_id": ObjectId(order_id), "restaurantId": restaurant_id},
        {"$set": {"status": "COMPLETED", "updatedAt": now}},
    )

    await publish_event(
        envelope(
            name="PaymentCompleted",
            restaurant_id=restaurant_id,
            payload={"orderId": order_id, "paymentId": str(doc["_id"]), "amount": amount},
        )
    )
    await publish_event(
        envelope(
            name="OrderUpdated",
            restaurant_id=restaurant_id,
            payload={"orderId": order_id, "status": "COMPLETED"},
        )
    )

    return {
        "id": str(doc["_id"]),
        "restaurantId": restaurant_id,
        "orderId": order_id,
        "method": method,
        "amount": amount,
        "status": doc["status"],
        "createdAt": now,
    }

