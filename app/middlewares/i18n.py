from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.user_service import user_service


class I18nMiddleware(BaseMiddleware):
    """Ensures the DB user exists and injects `language` + `db_user` into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None:
            db_user = await user_service.get_or_create(user.id, user.username, user.first_name)
            data["language"] = db_user.language
            data["db_user"] = db_user
        else:
            data["language"] = "fa"
        return await handler(event, data)
