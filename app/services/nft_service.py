from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import or_, select

from app.database.engine import get_session
from app.database.models import NftGift


@dataclass
class NftGiftData:
    slug: str
    name: str
    collection_name: str
    floor_price_ton: float
    last_sale_price_ton: float
    average_price_ton: float
    estimated_value_usd: float
    rarity_score: float


class NftService:
    """Telegram NFT Gift pricing service.

    IMPORTANT: Telegram does not expose an official public market-data API
    for NFT Gifts. Real prices are only visible on marketplaces such as
    Fragment, Portals and Tonnel, none of which currently offer a stable
    public API. This service is built around a local `nft_gifts` catalog
    (see NftGift model) that an admin job/script can populate and refresh
    periodically. Swap `_fetch_from_catalog` for a real HTTP provider here
    once a reliable data source is available -- the rest of the bot does
    not need to change.
    """

    async def search(self, query: str) -> list[NftGiftData]:
        q = f"%{query.strip().lower()}%"
        async with get_session() as session:
            stmt = select(NftGift).where(
                or_(
                    NftGift.name.ilike(q),
                    NftGift.collection_name.ilike(q),
                    NftGift.slug.ilike(q),
                )
            ).limit(5)
            rows = (await session.execute(stmt)).scalars().all()
        return [self._to_dataclass(r) for r in rows]

    async def get_by_slug(self, slug: str) -> NftGiftData | None:
        async with get_session() as session:
            row = await session.get(NftGift, slug)
        return self._to_dataclass(row) if row else None

    @staticmethod
    def _to_dataclass(row: NftGift) -> NftGiftData:
        return NftGiftData(
            slug=row.slug,
            name=row.name,
            collection_name=row.collection_name,
            floor_price_ton=row.floor_price_ton,
            last_sale_price_ton=row.last_sale_price_ton,
            average_price_ton=row.average_price_ton,
            estimated_value_usd=row.estimated_value_usd,
            rarity_score=row.rarity_score,
        )


nft_service = NftService()
