from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import AssetType
from app.locales import button


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang:fa"),
                InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en"),
            ]
        ]
    )


def asset_card_keyboard(language: str, asset_type: AssetType, asset_id: str, in_watchlist: bool) -> InlineKeyboardMarkup:
    watchlist_btn = (
        InlineKeyboardButton(text=button(language, "remove_watchlist"), callback_data=f"wl_del:{asset_type.value}:{asset_id}")
        if in_watchlist
        else InlineKeyboardButton(text=button(language, "add_watchlist"), callback_data=f"wl_add:{asset_type.value}:{asset_id}")
    )
    rows = [
        [watchlist_btn],
        [InlineKeyboardButton(text=button(language, "refresh"), callback_data=f"refresh:{asset_type.value}:{asset_id}")],
    ]
    if asset_type == AssetType.CRYPTO:
        rows.insert(1, [InlineKeyboardButton(text=button(language, "set_alert"), callback_data=f"alert_new:{asset_type.value}:{asset_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
