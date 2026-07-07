from __future__ import annotations

from dataclasses import dataclass

import aiohttp
from loguru import logger

from app.config import settings
from app.services.cache import cache_get_json, cache_set_json

COIN_LIST_CACHE_KEY = "crypto:coin_list"
MARKET_CACHE_PREFIX = "crypto:market:"


@dataclass
class CoinMarketData:
    id: str
    symbol: str
    name: str
    price_usd: float
    change_24h_percent: float
    market_cap: float
    volume_24h: float
    market_cap_rank: int | None
    circulating_supply: float | None
    ath: float
    atl: float


class CryptoService:
    """Wraps the public CoinGecko API with Redis caching."""

    def __init__(self) -> None:
        self._base_url = settings.coingecko_base_url
        self._headers = {}
        if settings.coingecko_api_key:
            self._headers["x-cg-demo-api-key"] = settings.coingecko_api_key

    async def _get(self, session: aiohttp.ClientSession, path: str, params: dict | None = None) -> dict | list | None:
        try:
            async with session.get(f"{self._base_url}{path}", params=params, headers=self._headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.warning(f"CoinGecko {path} returned {resp.status}")
                    return None
                return await resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"CoinGecko request failed for {path}: {exc}")
            return None

    async def get_coin_list(self, force_refresh: bool = False) -> list[dict]:
        """Returns [{id, symbol, name}, ...] for every coin listed on CoinGecko, cached."""
        if not force_refresh:
            cached = await cache_get_json(COIN_LIST_CACHE_KEY)
            if cached is not None:
                return cached

        async with aiohttp.ClientSession() as session:
            data = await self._get(session, "/coins/list")
        if not data:
            return []

        await cache_set_json(COIN_LIST_CACHE_KEY, data, settings.coin_list_ttl_seconds)
        return data

    async def search_coins(self, query: str) -> list[dict]:
        """Free-text search via CoinGecko's /search endpoint (handles fuzzy name/symbol matches)."""
        async with aiohttp.ClientSession() as session:
            data = await self._get(session, "/search", params={"query": query})
        if not data:
            return []
        return data.get("coins", [])

    async def get_coin_by_contract(self, platform: str, address: str) -> dict | None:
        async with aiohttp.ClientSession() as session:
            return await self._get(session, f"/coins/{platform}/contract/{address}")

    async def get_market_data(self, coin_id: str) -> CoinMarketData | None:
        cache_key = f"{MARKET_CACHE_PREFIX}{coin_id}"
        cached = await cache_get_json(cache_key)
        if cached:
            return CoinMarketData(**cached)

        async with aiohttp.ClientSession() as session:
            data = await self._get(
                session,
                "/coins/markets",
                params={
                    "vs_currency": "usd",
                    "ids": coin_id,
                    "price_change_percentage": "24h",
                },
            )
        if not data:
            return None

        row = data[0]
        result = CoinMarketData(
            id=row["id"],
            symbol=row["symbol"].upper(),
            name=row["name"],
            price_usd=row.get("current_price") or 0.0,
            change_24h_percent=row.get("price_change_percentage_24h") or 0.0,
            market_cap=row.get("market_cap") or 0.0,
            volume_24h=row.get("total_volume") or 0.0,
            market_cap_rank=row.get("market_cap_rank"),
            circulating_supply=row.get("circulating_supply"),
            ath=row.get("ath") or 0.0,
            atl=row.get("atl") or 0.0,
        )
        await cache_set_json(cache_key, result.__dict__, settings.cache_ttl_seconds)
        return result

    async def get_price_only(self, coin_id: str) -> float | None:
        data = await self.get_market_data(coin_id)
        return data.price_usd if data else None


crypto_service = CryptoService()
