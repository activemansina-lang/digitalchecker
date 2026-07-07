from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AssetType(str, enum.Enum):
    CRYPTO = "crypto"
    NFT_GIFT = "nft_gift"


class AlertCondition(str, enum.Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_UP = "percent_up"
    PERCENT_DOWN = "percent_down"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # telegram user id
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="fa", server_default="fa")
    is_bot_blocked: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    watchlist_items: Mapped[list["WatchlistItem"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    search_history: Mapped[list["SearchHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "asset_type", "asset_id", name="uq_watchlist_user_asset"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType))
    asset_id: Mapped[str] = mapped_column(String(128))  # coingecko id or nft gift slug
    display_name: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="watchlist_items")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType))
    asset_id: Mapped[str] = mapped_column(String(128))
    display_name: Mapped[str] = mapped_column(String(128))
    condition: Mapped[AlertCondition] = mapped_column(Enum(AlertCondition))
    target_value: Mapped[float] = mapped_column(Float)  # target price or target percent
    base_value: Mapped[float | None] = mapped_column(Float, nullable=True)  # price at creation time, for percent alerts
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.ACTIVE, server_default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="alerts")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    query: Mapped[str] = mapped_column(String(256))
    asset_type: Mapped[AssetType | None] = mapped_column(Enum(AssetType), nullable=True)
    asset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="search_history")


class NftGift(Base):
    """Local catalog of Telegram NFT Gifts.

    NOTE: There is no official public market API for Telegram NFT Gifts.
    This table is a pluggable data source seeded manually/by an admin job
    (e.g. periodic scraping of Portals/Tonnel/Fragment marketplaces) so the
    architecture is ready to plug a real provider in NftPriceProvider later.
    """

    __tablename__ = "nft_gifts"

    slug: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    collection_name: Mapped[str] = mapped_column(String(128))
    floor_price_ton: Mapped[float] = mapped_column(Float, default=0.0)
    last_sale_price_ton: Mapped[float] = mapped_column(Float, default=0.0)
    average_price_ton: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_value_usd: Mapped[float] = mapped_column(Float, default=0.0)
    rarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
