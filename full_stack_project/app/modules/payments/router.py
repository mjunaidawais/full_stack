from __future__ import annotations

from fastapi import APIRouter, Depends

from app.middlewares.rbac import CurrentUser, require_roles
from app.middlewares.tenant import get_restaurant_id
from app.modules.payments.models import CreatePaymentRequest, PaymentOut
from app.modules.payments.service import create_payment


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentOut)
async def create_payment_route(
    body: CreatePaymentRequest,
    restaurant_id: str = Depends(get_restaurant_id),
    user: CurrentUser = Depends(require_roles("counter", "admin")),
) -> PaymentOut:
    out = await create_payment(
        restaurant_id=restaurant_id, order_id=body.orderId, method=body.method, amount=body.amount
    )
    return PaymentOut(**out)

