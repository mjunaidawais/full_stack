from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PaymentMethod = Literal["cash", "card", "online"]
PaymentStatus = Literal["PENDING", "SUCCESS", "FAILED"]


class CreatePaymentRequest(BaseModel):
    orderId: str = Field(min_length=1)
    method: PaymentMethod
    amount: float = Field(gt=0)


class PaymentOut(BaseModel):
    id: str
    restaurantId: str
    orderId: str
    method: PaymentMethod
    amount: float
    status: PaymentStatus
    createdAt: int

