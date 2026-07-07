from __future__ import annotations

from sqlalchemy import select

from app.database.engine import get_session
from app.database.models import Alert, AlertCondition, AlertStatus, AssetType, WatchlistItem


class WatchlistService:
    async def add(self, user_id: int, asset_type: AssetType, asset_id: str, display_name: str) -> bool:
        async with get_session() as session:
            exists = await session.execute(
                select(WatchlistItem).where(
                    WatchlistItem.user_id == user_id,
                    WatchlistItem.asset_type == asset_type,
                    WatchlistItem.asset_id == asset_id,
                )
            )
            if exists.scalar_one_or_none():
                return False
            session.add(WatchlistItem(user_id=user_id, asset_type=asset_type, asset_id=asset_id, display_name=display_name))
            return True

    async def remove(self, user_id: int, asset_type: AssetType, asset_id: str) -> None:
        async with get_session() as session:
            item = await session.execute(
                select(WatchlistItem).where(
                    WatchlistItem.user_id == user_id,
                    WatchlistItem.asset_type == asset_type,
                    WatchlistItem.asset_id == asset_id,
                )
            )
            row = item.scalar_one_or_none()
            if row:
                await session.delete(row)

    async def list_for_user(self, user_id: int) -> list[WatchlistItem]:
        async with get_session() as session:
            result = await session.execute(select(WatchlistItem).where(WatchlistItem.user_id == user_id))
            return list(result.scalars().all())


class AlertService:
    async def create(
        self,
        user_id: int,
        asset_type: AssetType,
        asset_id: str,
        display_name: str,
        condition: AlertCondition,
        target_value: float,
        base_value: float | None = None,
    ) -> Alert:
        async with get_session() as session:
            alert = Alert(
                user_id=user_id,
                asset_type=asset_type,
                asset_id=asset_id,
                display_name=display_name,
                condition=condition,
                target_value=target_value,
                base_value=base_value,
                status=AlertStatus.ACTIVE,
            )
            session.add(alert)
            await session.flush()
            await session.refresh(alert)
            return alert

    async def list_active(self) -> list[Alert]:
        async with get_session() as session:
            result = await session.execute(select(Alert).where(Alert.status == AlertStatus.ACTIVE))
            return list(result.scalars().all())

    async def list_for_user(self, user_id: int) -> list[Alert]:
        async with get_session() as session:
            result = await session.execute(select(Alert).where(Alert.user_id == user_id))
            return list(result.scalars().all())

    async def mark_triggered(self, alert_id: int) -> None:
        from datetime import datetime, timezone

        async with get_session() as session:
            alert = await session.get(Alert, alert_id)
            if alert:
                alert.status = AlertStatus.TRIGGERED
                alert.triggered_at = datetime.now(timezone.utc)

    async def cancel(self, alert_id: int, user_id: int) -> bool:
        async with get_session() as session:
            alert = await session.get(Alert, alert_id)
            if alert and alert.user_id == user_id and alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.CANCELLED
                return True
        return False


watchlist_service = WatchlistService()
alert_service = AlertService()
