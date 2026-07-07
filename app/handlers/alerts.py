from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.models import AlertCondition, AssetType
from app.handlers.states import AlertCreationStates
from app.locales import t
from app.services.alert_service import alert_service
from app.services.crypto_service import crypto_service

router = Router(name="alerts")


@router.callback_query(F.data.startswith("alert_new:"))
async def start_alert_creation(callback: CallbackQuery, language: str, state: FSMContext) -> None:
    _, asset_type_raw, asset_id = callback.data.split(":", 2)
    data = await crypto_service.get_market_data(asset_id)
    if not data:
        await callback.answer()
        return

    await state.update_data(asset_type=asset_type_raw, asset_id=asset_id, display_name=data.name, current_price=data.price_usd)
    await state.set_state(AlertCreationStates.waiting_for_target_price)
    await callback.message.answer(t(language, "alert_prompt", name=data.name), parse_mode="HTML")
    await callback.answer()


@router.message(AlertCreationStates.waiting_for_target_price, F.text)
async def receive_target_price(message: Message, language: str, state: FSMContext) -> None:
    raw = message.text.strip().replace(",", "")
    try:
        target_price = float(raw)
    except ValueError:
        await message.answer(t(language, "alert_invalid_number"))
        return

    fsm_data = await state.get_data()
    asset_type = AssetType(fsm_data["asset_type"])
    asset_id = fsm_data["asset_id"]
    display_name = fsm_data["display_name"]
    current_price = fsm_data["current_price"]

    condition = AlertCondition.PRICE_ABOVE if target_price >= current_price else AlertCondition.PRICE_BELOW

    await alert_service.create(
        user_id=message.from_user.id,
        asset_type=asset_type,
        asset_id=asset_id,
        display_name=display_name,
        condition=condition,
        target_value=target_price,
        base_value=current_price,
    )
    await state.clear()
    await message.answer(t(language, "alert_created", name=display_name, target=target_price), parse_mode="HTML")


@router.message(Command("alerts"))
async def cmd_list_alerts(message: Message, language: str) -> None:
    alerts = await alert_service.list_for_user(message.from_user.id)
    active = [a for a in alerts if a.status.value == "active"]
    if not active:
        await message.answer(t(language, "alerts_empty"))
        return
    lines = [t(language, "alerts_list_title")]
    for a in active:
        arrow = "≥" if a.condition == AlertCondition.PRICE_ABOVE else "≤"
        lines.append(f"🔔 {a.display_name} {arrow} ${a.target_value:,.4f}")
    await message.answer("\n".join(lines), parse_mode="HTML")
