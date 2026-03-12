import uuid
from datetime import date
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import DailyStatRepository
from app.models.daily_stat import DailyStat


class SQLAlchemyDailyStatRepository(DailyStatRepository):
    """A repository implementation for DailyStat entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, stat: DailyStat) -> DailyStat:
        self.db.add(stat)
        try:
            await self.db.commit()
            await self.db.refresh(stat)
            return stat
        except IntegrityError:
            await self.db.rollback()
            raise

    @override
    async def get_by_monitor_and_date(
        self, monitor_id: uuid.UUID, date: date
    ) -> DailyStat | None:
        result = await self.db.execute(
            select(DailyStat).where(
                DailyStat.monitor_id == monitor_id,
                DailyStat.date == date,
            )
        )
        return result.scalars().first()

    @override
    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[DailyStat]:
        result = await self.db.execute(
            select(DailyStat).where(DailyStat.monitor_id == monitor_id)
        )
        return list(result.scalars().all())
