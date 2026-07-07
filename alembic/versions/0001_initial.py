"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-07

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

asset_type_enum = sa.Enum("crypto", "nft_gift", name="assettype")
alert_condition_enum = sa.Enum("price_above", "price_below", "percent_up", "percent_down", name="alertcondition")
alert_status_enum = sa.Enum("active", "triggered", "cancelled", name="alertstatus")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("language", sa.String(8), nullable=False, server_default="fa"),
        sa.Column("is_bot_blocked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "nft_gifts",
        sa.Column("slug", sa.String(128), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("collection_name", sa.String(128), nullable=False),
        sa.Column("floor_price_ton", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_sale_price_ton", sa.Float(), nullable=False, server_default="0"),
        sa.Column("average_price_ton", sa.Float(), nullable=False, server_default="0"),
        sa.Column("estimated_value_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("rarity_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_type", asset_type_enum, nullable=False),
        sa.Column("asset_id", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "asset_type", "asset_id", name="uq_watchlist_user_asset"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_type", asset_type_enum, nullable=False),
        sa.Column("asset_id", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("condition", alert_condition_enum, nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("base_value", sa.Float(), nullable=True),
        sa.Column("status", alert_status_enum, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("query", sa.String(256), nullable=False),
        sa.Column("asset_type", asset_type_enum, nullable=True),
        sa.Column("asset_id", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("ix_watchlist_user", "watchlist_items", ["user_id"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_user", "alerts", ["user_id"])
    op.create_index("ix_search_history_user", "search_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_search_history_user", table_name="search_history")
    op.drop_index("ix_alerts_user", table_name="alerts")
    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_index("ix_watchlist_user", table_name="watchlist_items")
    op.drop_table("search_history")
    op.drop_table("alerts")
    op.drop_table("watchlist_items")
    op.drop_table("nft_gifts")
    op.drop_table("users")
    asset_type_enum.drop(op.get_bind(), checkfirst=True)
    alert_condition_enum.drop(op.get_bind(), checkfirst=True)
    alert_status_enum.drop(op.get_bind(), checkfirst=True)
