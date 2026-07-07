from __future__ import annotations

from app.config import settings
from app.database.engine import get_session
from app.database.models import User


class UserService:
    async def get_or_create(self, telegram_id: int, username: str | None, first_name: str | None) -> User:
        async with get_session() as session:
            user = await session.get(User, telegram_id)
            if user is None:
                user = User(
                    id=telegram_id,
                    username=username,
                    first_name=first_name,
                    language=settings.default_language,
                )
                session.add(user)
                await session.flush()
            else:
                user.username = username
                user.first_name = first_name
            await session.refresh(user)
            return user

    async def set_language(self, telegram_id: int, language: str) -> None:
        async with get_session() as session:
            user = await session.get(User, telegram_id)
            if user:
                user.language = language

    async def get_language(self, telegram_id: int) -> str:
        async with get_session() as session:
            user = await session.get(User, telegram_id)
            return user.language if user else settings.default_language


user_service = UserService()
