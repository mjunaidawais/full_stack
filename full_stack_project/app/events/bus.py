from __future__ import annotations

import json
import time
from typing import Any, Awaitable, Callable

from redis.asyncio.client import PubSub

from app.db.redis import redis_client
from app.events.types import EventEnvelope, EventName


CHANNEL = "events"


def envelope(*, name: EventName, restaurant_id: str, payload: dict[str, Any]) -> EventEnvelope:
    return {
        "name": name,
        "restaurantId": restaurant_id,
        "payload": payload,
        "ts": int(time.time()),
    }


async def publish_event(env: EventEnvelope) -> None:
    await redis_client().publish(CHANNEL, json.dumps(env))


async def subscribe_events(
    handler: Callable[[EventEnvelope], Awaitable[None]],
) -> tuple[Callable[[], Awaitable[None]], Callable[[], Awaitable[None]]]:
    r = redis_client()
    ps: PubSub = r.pubsub()
    await ps.subscribe(CHANNEL)
    running = True

    async def loop() -> None:
        nonlocal running
        while running:
            msg = await ps.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if not msg:
                continue
            try:
                env = json.loads(msg["data"])
            except Exception:
                continue
            if isinstance(env, dict) and "name" in env and "restaurantId" in env and "payload" in env:
                await handler(env)  # type: ignore[arg-type]

    async def stop() -> None:
        nonlocal running
        running = False
        await ps.unsubscribe(CHANNEL)
        await ps.close()

    return loop, stop

