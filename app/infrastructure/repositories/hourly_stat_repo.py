import uuid
from datetime import datetime
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import HourlyStatRepository
from app.models.hourly_stat import HourlyStat


class SQLAlchemyHourlyStatRepository(HourlyStatRepository):
    """A repository implementation for HourlyStat entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, stat: HourlyStat) -> HourlyStat:
        self.db.add(stat)
        try:
            await self.db.commit()
            await self.db.refresh(stat)
            return stat
        except IntegrityError:
            await self.db.rollback()
            raise

    @override
    async def get_by_monitor_and_hour(
        self, monitor_id: uuid.UUID, hour_timestamp: datetime
    ) -> HourlyStat | None:
        result = await self.db.execute(
            select(HourlyStat).where(
                HourlyStat.monitor_id == monitor_id,
                HourlyStat.hour_timestamp == hour_timestamp,
            )
        )
        return result.scalars().first()

    @override
    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[HourlyStat]:
        result = await self.db.execute(
            select(HourlyStat).where(HourlyStat.monitor_id == monitor_id)
        )
        return list(result.scalars().all())
