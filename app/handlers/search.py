from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from app.database.models import AssetType
from app.database.engine import get_session
from app.database.models import SearchHistory
from app.keyboards.inline import asset_card_keyboard
from app.locales import t
from app.services.alert_service import watchlist_service
from app.services.crypto_service import crypto_service
from app.services.nft_service import nft_service
from app.services.search_service import search_service
from app.utils.formatting import format_crypto_card, format_nft_card

router = Router(name="search")


async def _is_in_watchlist(user_id: int, asset_type: AssetType, asset_id: str) -> bool:
    items = await watchlist_service.list_for_user(user_id)
    return any(i.asset_type == asset_type and i.asset_id == asset_id for i in items)


async def _log_search(user_id: int, query: str, asset_type: AssetType | None, asset_id: str | None) -> None:
    try:
        async with get_session() as session:
            session.add(SearchHistory(user_id=user_id, query=query[:256], asset_type=asset_type, asset_id=asset_id))
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Failed to log search history: {exc}")


@router.message(F.text, ~F.text.startswith("/"))
async def handle_free_text(message: Message, language: str, state: FSMContext) -> None:
    # If the user is in the middle of setting an alert, let alerts.py handle the number input.
    current_state = await state.get_state()
    if current_state is not None:
        return

    query = message.text.strip()
    if len(query) < 2 or len(query) > 64:
        return  # ignore noise in groups

    try:
        result = await search_service.classify(query)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Search classify failed for '{query}': {exc}")
        await message.answer(t(language, "searching_error"))
        return

    if result.asset_type is None:
        await _log_search(message.from_user.id, query, None, None)
        await message.answer(t(language, "not_found", query=query))
        return

    await _log_search(message.from_user.id, query, result.asset_type, result.asset_id)

    if result.asset_type == AssetType.CRYPTO:
        data = await crypto_service.get_market_data(result.asset_id)
        if not data:
            await message.answer(t(language, "not_found", query=query))
            return
        in_wl = await _is_in_watchlist(message.from_user.id, AssetType.CRYPTO, data.id)
        await message.answer(
            format_crypto_card(language, data),
            parse_mode="HTML",
            reply_markup=asset_card_keyboard(language, AssetType.CRYPTO, data.id, in_wl),
        )
    else:
        data = await nft_service.get_by_slug(result.asset_id)
        if not data:
            await message.answer(t(language, "not_found", query=query))
            return
        in_wl = await _is_in_watchlist(message.from_user.id, AssetType.NFT_GIFT, data.slug)
        await message.answer(
            format_nft_card(language, data),
            parse_mode="HTML",
            reply_markup=asset_card_keyboard(language, AssetType.NFT_GIFT, data.slug, in_wl),
        )


@router.callback_query(F.data.startswith("refresh:"))
async def handle_refresh(callback, language: str) -> None:  # noqa: ANN001
    _, asset_type_raw, asset_id = callback.data.split(":", 2)
    asset_type = AssetType(asset_type_raw)

    if asset_type == AssetType.CRYPTO:
        data = await crypto_service.get_market_data(asset_id)
        if data:
            in_wl = await _is_in_watchlist(callback.from_user.id, asset_type, asset_id)
            await callback.message.edit_text(
                format_crypto_card(language, data),
                parse_mode="HTML",
                reply_markup=asset_card_keyboard(language, asset_type, asset_id, in_wl),
            )
    else:
        data = await nft_service.get_by_slug(asset_id)
        if data:
            in_wl = await _is_in_watchlist(callback.from_user.id, asset_type, asset_id)
            await callback.message.edit_text(
                format_nft_card(language, data),
                parse_mode="HTML",
                reply_markup=asset_card_keyboard(language, asset_type, asset_id, in_wl),
            )
    await callback.answer()
