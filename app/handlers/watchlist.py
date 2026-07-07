from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.database.models import AssetType
from app.keyboards.inline import asset_card_keyboard
from app.locales import t
from app.services.alert_service import watchlist_service
from app.services.crypto_service import crypto_service
from app.services.nft_service import nft_service

router = Router(name="watchlist")


@router.message(Command("watchlist"))
async def cmd_watchlist(message: Message, language: str) -> None:
    items = await watchlist_service.list_for_user(message.from_user.id)
    if not items:
        await message.answer(t(language, "watchlist_empty"))
        return
    lines = [t(language, "watchlist_title")]
    for item in items:
        icon = "💰" if item.asset_type == AssetType.CRYPTO else "🎁"
        lines.append(f"{icon} {item.display_name}")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.callback_query(F.data.startswith("wl_add:"))
async def handle_add_watchlist(callback: CallbackQuery, language: str) -> None:
    _, asset_type_raw, asset_id = callback.data.split(":", 2)
    asset_type = AssetType(asset_type_raw)

    if asset_type == AssetType.CRYPTO:
        data = await crypto_service.get_market_data(asset_id)
        display_name = data.name if data else asset_id
    else:
        data = await nft_service.get_by_slug(asset_id)
        display_name = data.name if data else asset_id

    added = await watchlist_service.add(callback.from_user.id, asset_type, asset_id, display_name)
    await callback.answer(t(language, "added_to_watchlist" if added else "already_in_watchlist"), show_alert=True)

    in_wl = True
    await callback.message.edit_reply_markup(reply_markup=asset_card_keyboard(language, asset_type, asset_id, in_wl))


@router.callback_query(F.data.startswith("wl_del:"))
async def handle_remove_watchlist(callback: CallbackQuery, language: str) -> None:
    _, asset_type_raw, asset_id = callback.data.split(":", 2)
    asset_type = AssetType(asset_type_raw)

    await watchlist_service.remove(callback.from_user.id, asset_type, asset_id)
    await callback.answer(t(language, "removed_from_watchlist"), show_alert=True)

    await callback.message.edit_reply_markup(reply_markup=asset_card_keyboard(language, asset_type, asset_id, False))
