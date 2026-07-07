from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import settings
from app.locales import t

router = Router(name="help_support")


@router.message(Command("help"))
async def cmd_help(message: Message, language: str) -> None:
    await message.answer(t(language, "help"), parse_mode="HTML")


@router.message(Command("support"))
async def cmd_support(message: Message, language: str) -> None:
    await message.answer(t(language, "support", link=settings.support_chat_link), parse_mode="HTML")
