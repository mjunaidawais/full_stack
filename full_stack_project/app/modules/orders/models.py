from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


OrderStatus = Literal["PLACED", "PREPARING", "READY", "COMPLETED", "CANCELLED"]


class OrderItemIn(BaseModel):
    productId: str = Field(min_length=1)
    qty: int = Field(ge=1)


class CreateOrderRequest(BaseModel):
    tableNumber: str = Field(min_length=1)
    items: list[OrderItemIn] = Field(min_length=1)
    idempotencyKey: str = Field(min_length=8)


class OrderOut(BaseModel):
    id: str
    restaurantId: str
    tableNumber: str
    items: list[OrderItemIn]
    status: OrderStatus
    createdBy: str
    createdAt: int
    updatedAt: int


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus

