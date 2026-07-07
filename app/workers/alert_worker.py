from __future__ import annotations

import asyncio

from aiogram import Bot
from loguru import logger

from app.config import settings
from app.database.models import AlertCondition, AssetType
from app.locales import t
from app.services.alert_service import alert_service
from app.services.crypto_service import crypto_service
from app.services.user_service import user_service


def _condition_met(condition: AlertCondition, target: float, base: float | None, current: float) -> bool:
    if condition == AlertCondition.PRICE_ABOVE:
        return current >= target
    if condition == AlertCondition.PRICE_BELOW:
        return current <= target
    if condition == AlertCondition.PERCENT_UP and base:
        return current >= base * (1 + target / 100)
    if condition == AlertCondition.PERCENT_DOWN and base:
        return current <= base * (1 - target / 100)
    return False


async def check_alerts_once(bot: Bot) -> None:
    active_alerts = await alert_service.list_active()
    if not active_alerts:
        return

    # Group by asset to avoid redundant API calls when many users watch the same coin.
    price_cache: dict[str, float | None] = {}

    for alert in active_alerts:
        if alert.asset_type != AssetType.CRYPTO:
            continue  # NFT gift alerts rely on the local catalog refresh job, not live polling

        if alert.asset_id not in price_cache:
            data = await crypto_service.get_market_data(alert.asset_id)
            price_cache[alert.asset_id] = data.price_usd if data else None

        current_price = price_cache[alert.asset_id]
        if current_price is None:
            continue

        if _condition_met(alert.condition, alert.target_value, alert.base_value, current_price):
            language = await user_service.get_language(alert.user_id)
            try:
                await bot.send_message(
                    alert.user_id,
                    t(language, "alert_triggered", name=alert.display_name, target=alert.target_value, current=current_price),
                    parse_mode="HTML",
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Failed to notify user {alert.user_id} about alert {alert.id}: {exc}")
            await alert_service.mark_triggered(alert.id)


async def run_alert_worker(bot: Bot) -> None:
    logger.info("Alert worker started")
    while True:
        try:
            await check_alerts_once(bot)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Alert worker iteration failed: {exc}")
        await asyncio.sleep(settings.alert_check_interval_seconds)
