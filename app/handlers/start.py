from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.keyboards.inline import language_keyboard
from app.locales import t
from app.services.user_service import user_service

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, language: str) -> None:
    await message.answer(t(language, "welcome"), parse_mode="HTML")
    await message.answer(t(language, "choose_language"), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery, language: str) -> None:
    new_lang = callback.data.split(":")[1]
    await user_service.set_language(callback.from_user.id, new_lang)
    await callback.message.edit_text(t(new_lang, "language_set"))
    await callback.answer()
