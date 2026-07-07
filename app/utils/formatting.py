from __future__ import annotations

from app.locales import t
from app.services.crypto_service import CoinMarketData
from app.services.nft_service import NftGiftData


def format_supply(value: float | None) -> str:
    if value is None:
        return "N/A"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:.2f}"


def format_crypto_card(language: str, data: CoinMarketData) -> str:
    change_emoji = "🟢" if data.change_24h_percent >= 0 else "🔴"
    return t(
        language,
        "crypto_card",
        name=data.name,
        symbol=data.symbol,
        price=data.price_usd,
        change=data.change_24h_percent,
        change_emoji=change_emoji,
        rank=data.market_cap_rank or "N/A",
        market_cap=data.market_cap,
        volume=data.volume_24h,
        supply=format_supply(data.circulating_supply),
        ath=data.ath,
        atl=data.atl,
    )


def format_nft_card(language: str, data: NftGiftData) -> str:
    return t(
        language,
        "nft_card",
        name=data.name,
        collection=data.collection_name,
        floor=data.floor_price_ton,
        last_sale=data.last_sale_price_ton,
        average=data.average_price_ton,
        estimated_usd=data.estimated_value_usd,
        rarity=data.rarity_score,
    )
