from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.config import settings
from app.services.cache import redis


class ThrottlingMiddleware(BaseMiddleware):
    """Simple per-user rate limiter backed by Redis, protects the bot & upstream APIs."""

    def __init__(self, rate_limit_per_second: float | None = None) -> None:
        self._min_interval = 1.0 / (rate_limit_per_second or settings.rate_limit_per_second)
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        key = f"throttle:{user.id}"
        now = time.monotonic()
        last_call = await redis.get(key)
        if last_call is not None and now - float(last_call) < self._min_interval:
            return None  # silently drop to avoid spamming the user with rate-limit messages
        await redis.set(key, str(now), ex=5)
        return await handler(event, data)
