import uuid
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import (
    AlertChannelAlreadyLinkedError,
    AppError,
    DatabaseError,
    MonitorNotFoundError,
)
from app.core.result import Err, Ok, Result
from app.domain.repositories import MonitorRepository
from app.models.alert_channel import AlertChannel
from app.models.monitor import Monitor
from app.models.monitor_channel import MonitorChannel


class SQLAlchemyMonitorRepository(MonitorRepository):
    """A repository implementation for Monitor entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, monitor: Monitor) -> Result[Monitor, AppError]:
        self.db.add(monitor)

        try:
            await self.db.commit()
            await self.db.refresh(monitor)
            return Ok(monitor)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_id(
        self, monitor_id: uuid.UUID, *, load_channels: bool = False
    ) -> Result[Monitor, AppError]:
        query = select(Monitor).where(
            Monitor.id == monitor_id, Monitor.deleted_at.is_(None)
        )
        if load_channels:
            query = query.options(selectinload(Monitor.alert_channels))
        result = await self.db.execute(query)

        monitor = result.scalars().first()
        if not monitor:
            return Err(MonitorNotFoundError(monitor_id=monitor_id))
        return Ok(monitor)

    @override
    async def get_all_active(self) -> Result[list[Monitor], AppError]:
        result = await self.db.execute(
            select(Monitor).where(
                Monitor.is_paused.is_(False), Monitor.deleted_at.is_(None)
            )
        )
        return Ok(list(result.scalars().all()))

    @override
    async def get_all_by_user(
        self, user_id: uuid.UUID
    ) -> Result[list[Monitor], AppError]:
        result = await self.db.execute(
            select(Monitor).where(
                Monitor.user_id == user_id, Monitor.deleted_at.is_(None)
            )
        )
        return Ok(list(result.scalars().all()))

    @override
    async def add_alert_channel(
        self, monitor_id: uuid.UUID, channel: AlertChannel
    ) -> Result[None, AppError]:
        """Add an alert channel to a monitor if it's not already linked."""

        new_monitor_channel = MonitorChannel(
            monitor_id=monitor_id, alert_channel_id=channel.id
        )
        self.db.add(new_monitor_channel)

        try:
            await self.db.commit()
            return Ok(None)
        except IntegrityError as e:
            await self.db.rollback()
            if (
                hasattr(e.orig, "pgcode")
                and e.orig.pgcode == "23505"  # Unique violation
            ):
                return Err(AlertChannelAlreadyLinkedError())
            return Err(DatabaseError(detail=str(e)))
