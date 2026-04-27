from __future__ import annotations

import asyncio
from typing import Any, Callable

import socketio

from app.events.bus import subscribe_events
from app.events.types import EventEnvelope


def create_socket_server() -> socketio.AsyncServer:
    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

    @sio.event
    async def connect(sid: str, environ: dict, auth: dict | None) -> bool:
        # Clients should send restaurantId + role + userId (or a JWT) in production.
        # For scaffold: accept connection and allow explicit room join.
        return True

    @sio.event
    async def join_room(sid: str, data: dict[str, Any]) -> None:
        room = str(data.get("room", ""))
        if room:
            await sio.enter_room(sid, room)

    @sio.event
    async def leave_room(sid: str, data: dict[str, Any]) -> None:
        room = str(data.get("room", ""))
        if room:
            await sio.leave_room(sid, room)

    async def on_event(env: EventEnvelope) -> None:
        restaurant_id = env["restaurantId"]
        name = env["name"]

        # Multi-tenant broadcast: always emit to tenant-scoped rooms.
        await sio.emit(name, env, room=f"restaurant_{restaurant_id}")

        # Convenience rooms matching your architecture diagram (optional).
        payload = env.get("payload", {})
        await sio.emit(name, env, room=f"{restaurant_id}_kitchen_room")
        await sio.emit(name, env, room=f"{restaurant_id}_counter_room")

        waiter_id = payload.get("waiterId") or payload.get("createdBy")
        if waiter_id:
            await sio.emit(name, env, room=f"{restaurant_id}_waiter_{waiter_id}")

    async def start_redis_bridge() -> Callable[[], Any]:
        running = True
        active_stop: Callable[[], Any] | None = None

        async def runner() -> None:
            nonlocal active_stop
            while running:
                try:
                    loop_fn, stop_fn = await subscribe_events(on_event)
                    active_stop = stop_fn
                    await loop_fn()
                except asyncio.CancelledError:
                    return
                except Exception:
                    # Redis may not be up yet; retry with backoff.
                    await asyncio.sleep(2)

        async def stop() -> None:
            nonlocal running
            running = False
            if active_stop:
                try:
                    await active_stop()
                except Exception:
                    pass
            task.cancel()

        task = asyncio.create_task(runner())
        return stop

    sio.start_redis_bridge = start_redis_bridge  # type: ignore[attr-defined]
    return sio

