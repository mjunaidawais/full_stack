from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.middlewares.rbac import CurrentUser, require_roles
from app.middlewares.tenant import get_restaurant_id
from app.modules.orders.models import CreateOrderRequest, OrderOut, UpdateOrderStatusRequest
from app.modules.orders.service import create_order, list_orders, update_status


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/create", response_model=OrderOut)
async def create_order_route(
    body: CreateOrderRequest,
    restaurant_id: str = Depends(get_restaurant_id),
    user: CurrentUser = Depends(require_roles("waiter", "admin")),
) -> OrderOut:
    out = await create_order(restaurant_id=restaurant_id, user=user, body=body.model_dump())
    return OrderOut(**out)


@router.get("", response_model=list[OrderOut])
async def list_orders_route(
    restaurant_id: str = Depends(get_restaurant_id),
    user: CurrentUser = Depends(require_roles("admin", "kitchen", "counter", "waiter")),
    status: Annotated[str | None, Query()] = None,
) -> list[OrderOut]:
    items = await list_orders(restaurant_id=restaurant_id, status=status)
    return [OrderOut(**x) for x in items]


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_status_route(
    order_id: str,
    body: UpdateOrderStatusRequest,
    restaurant_id: str = Depends(get_restaurant_id),
    user: CurrentUser = Depends(require_roles("kitchen", "admin", "counter")),
) -> OrderOut:
    out = await update_status(
        restaurant_id=restaurant_id, order_id=order_id, status=body.status, user=user
    )
    return OrderOut(**out)

