from __future__ import annotations

import json
from typing import Any

from redis.asyncio import ConnectionPool, Redis

from app.config import settings

_pool = ConnectionPool.from_url(settings.redis_url, decode_responses=True, max_connections=50)
redis: Redis = Redis(connection_pool=_pool)


async def cache_get_json(key: str) -> Any | None:
    raw = await redis.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    await redis.set(key, json.dumps(value), ex=ttl_seconds)


async def cache_close() -> None:
    await redis.aclose()
