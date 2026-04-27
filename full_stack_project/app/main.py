from __future__ import annotations

from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.mongo import close_mongo
from app.db.redis import close_redis
from app.events.socket import create_socket_server
from app.modules.auth.router import router as auth_router
from app.modules.orders.router import router as orders_router
from app.modules.payments.router import router as payments_router


# Single Socket.IO server instance for the whole process.
sio_server: socketio.AsyncServer = create_socket_server()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Redis->Socket bridge
    stop_bridge = await sio_server.start_redis_bridge()  # type: ignore[attr-defined]
    app.state.stop_bridge = stop_bridge

    try:
        yield
    finally:
        try:
            await app.state.stop_bridge()
        except Exception:
            pass
        await close_redis()
        await close_mongo()


fastapi_app = FastAPI(title=settings.app_name, lifespan=lifespan)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list() or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(auth_router)
fastapi_app.include_router(orders_router)
fastapi_app.include_router(payments_router)

# Socket.IO ASGI app mounted at root alongside FastAPI.
socket_app = socketio.ASGIApp(sio_server, other_asgi_app=fastapi_app)

# Export `app` for uvicorn
app = socket_app

