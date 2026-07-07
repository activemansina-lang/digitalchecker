"""One-off script to seed/refresh the local NFT Gift catalog.

Run manually or on a schedule (e.g. Railway cron) once you have a real data
source; for now it seeds a few well-known Telegram NFT Gifts with
placeholder figures so the bot has something to demo.

Usage:
    python -m scripts.seed_nft_gifts
"""
from __future__ import annotations

import asyncio

from sqlalchemy.dialects.postgresql import insert

from app.database.engine import get_session
from app.database.models import NftGift

SEED_DATA = [
    dict(
        slug="plush-pepe",
        name="Plush Pepe",
        collection_name="Plush Pepe",
        floor_price_ton=45000.0,
        last_sale_price_ton=46500.0,
        average_price_ton=45800.0,
        estimated_value_usd=210000.0,
        rarity_score=99.9,
    ),
    dict(
        slug="durovs-cap",
        name="Durov's Cap",
        collection_name="Durov's Cap",
        floor_price_ton=12000.0,
        last_sale_price_ton=12500.0,
        average_price_ton=12100.0,
        estimated_value_usd=55000.0,
        rarity_score=98.5,
    ),
    dict(
        slug="loot-bag",
        name="Loot Bag",
        collection_name="Loot Bag",
        floor_price_ton=350.0,
        last_sale_price_ton=360.0,
        average_price_ton=355.0,
        estimated_value_usd=1600.0,
        rarity_score=70.0,
    ),
]


async def seed() -> None:
    async with get_session() as session:
        for item in SEED_DATA:
            stmt = insert(NftGift).values(**item)
            stmt = stmt.on_conflict_do_update(index_elements=["slug"], set_=item)
            await session.execute(stmt)
    print(f"Seeded {len(SEED_DATA)} NFT gifts.")


if __name__ == "__main__":
    asyncio.run(seed())
