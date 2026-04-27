from __future__ import annotations

from typing import Literal, TypedDict


EventName = Literal["OrderCreated", "OrderUpdated", "OrderCancelled", "PaymentCompleted", "InventoryLow"]


class EventEnvelope(TypedDict):
    name: EventName
    restaurantId: str
    payload: dict
    ts: int

