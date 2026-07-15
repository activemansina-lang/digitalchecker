from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import get_close_matches

from app.database.models import AssetType
from app.services.cache import cache_get_json, cache_set_json
from app.services.crypto_service import crypto_service
from app.services.nft_service import nft_service

ALIAS_CACHE_KEY = "search:fa_alias_map"

# Curated Persian-name -> CoinGecko-id aliases for the most commonly requested coins.
# The generic CoinGecko /search endpoint already covers English name/symbol matches,
# so this map only needs to carry the Persian spellings.
FA_ALIASES: dict[str, str] = {
    "بیت کوین": "bitcoin",
    "بیتکوین": "bitcoin",
    "بیت‌کوین": "bitcoin",
    "اتریوم": "ethereum",
    "اتر": "ethereum",
    "تون": "the-open-network",
    "تون کوین": "the-open-network",
    "ترون": "tron",
    "دوج": "dogecoin",
    "دوج کوین": "dogecoin",
    "دوجکوین": "dogecoin",
    "پپه": "pepe",
    "سولانا": "solana",
    "بایננس کوین": "binancecoin",
    "بی ان بی": "binancecoin",
    "ریپل": "ripple",
    "ایکس آر پی": "ripple",
    "کاردانو": "cardano",
    "پولکادات": "polkadot",
    "لایت کوین": "litecoin",
    "شیبا": "shiba-inu",
    "شیبا اینو": "shiba-inu",
    "تتر": "tether",
    "یو اس دی سی": "usd-coin",
    "بایننس": "binancecoin",
    "تون کوین شبکه باز": "the-open-network",
}

# Contract addresses: ETH/BSC-style 0x... or long base58-ish strings.
_CONTRACT_RE = re.compile(r"^(0x[a-fA-F0-9]{20,64}|[A-Za-z0-9]{32,64})$")


@dataclass
class SearchResult:
    asset_type: AssetType | None
    asset_id: str | None
    display_name: str | None
    raw_matches: list[dict] | None = None


class SearchService:
    def _normalize(self, text: str) -> str:
        return text.strip().lower().replace("‌", " ").replace("  ", " ")

    def _match_fa_alias(self, text: str) -> str | None:
        norm = self._normalize(text)
        if norm in FA_ALIASES:
            return FA_ALIASES[norm]
        # fuzzy match against Persian aliases for small typos
        close = get_close_matches(norm, FA_ALIASES.keys(), n=1, cutoff=0.82)
        return FA_ALIASES[close[0]] if close else None

    async def classify(self, query: str) -> SearchResult:
        text = query.strip()
        if not text:
            return SearchResult(None, None, None)

        # 1) contract address lookup (assume Ethereum mainnet as default platform)
        if _CONTRACT_RE.match(text):
            coin = await crypto_service.get_coin_by_contract("ethereum", text)
            if coin:
                return SearchResult(AssetType.CRYPTO, coin["id"], coin.get("name", coin["id"]))

        # 2) Persian alias map (exact/fuzzy)
        fa_match = self._match_fa_alias(text)
        if fa_match:
            return SearchResult(AssetType.CRYPTO, fa_match, fa_match)

        # 3) CoinGecko fuzzy search (covers English names/symbols, e.g. btc, eth, doge)
        coins = await crypto_service.search_coins(text)
        if coins:
            best = coins[0]
            return SearchResult(AssetType.CRYPTO, best["id"], best.get("name", best["id"]), raw_matches=coins[:5])

        # 4) NFT gift catalog
        nft_matches = await nft_service.search(text)
        if nft_matches:
            best_nft = nft_matches[0]
            return SearchResult(AssetType.NFT_GIFT, best_nft.slug, best_nft.name)

        return SearchResult(None, None, None)


search_service = SearchService()
