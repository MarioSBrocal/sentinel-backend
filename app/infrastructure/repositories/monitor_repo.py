import uuid
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.repositories import MonitorRepository
from app.models.alert_channel import AlertChannel
from app.models.monitor import Monitor


class SQLAlchemyMonitorRepository(MonitorRepository):
    """A repository implementation for Monitor entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, monitor: Monitor) -> Monitor:
        self.db.add(monitor)
        try:
            await self.db.commit()
            await self.db.refresh(monitor)
            return monitor
        except IntegrityError:
            await self.db.rollback()
            raise

    @override
    async def get_by_id(self, monitor_id: uuid.UUID) -> Monitor | None:
        result = await self.db.execute(
            select(Monitor).where(
                Monitor.id == monitor_id, Monitor.deleted_at.is_(None)
            )
        )
        return result.scalars().first()

    @override
    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Monitor]:
        result = await self.db.execute(
            select(Monitor).where(
                Monitor.user_id == user_id, Monitor.deleted_at.is_(None)
            )
        )
        return list(result.scalars().all())

    @override
    async def add_alert_channel(
        self, monitor_id: uuid.UUID, channel: AlertChannel
    ) -> None:
        """Add an alert channel to a monitor if it's not already linked."""

        query = (
            select(Monitor)
            .where(Monitor.id == monitor_id, Monitor.deleted_at.is_(None))
            .options(selectinload(Monitor.alert_channels))
        )
        result = await self.db.execute(query)
        monitor = result.scalars().first()

        if monitor:
            if channel not in monitor.alert_channels:
                monitor.alert_channels.append(channel)
                await self.db.commit()
