from __future__ import annotations

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from app.core.config import settings

_client: AsyncMongoClient | None = None


def mongo_client() -> AsyncMongoClient:
    global _client
    if _client is None:
        _client = AsyncMongoClient(settings.mongodb_uri)
    return _client


def mongo_db() -> AsyncDatabase:
    return mongo_client()[settings.mongodb_db]


async def close_mongo() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None

