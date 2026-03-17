import uuid
from datetime import date
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, DailyStatNotFound, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import DailyStatRepository
from app.models.daily_stat import DailyStat


class SQLAlchemyDailyStatRepository(DailyStatRepository):
    """A repository implementation for DailyStat entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, stat: DailyStat) -> Result[DailyStat, AppError]:
        self.db.add(stat)

        try:
            await self.db.commit()
            await self.db.refresh(stat)
            return Ok(stat)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_monitor_and_date(
        self, monitor_id: uuid.UUID, date: date
    ) -> Result[DailyStat, AppError]:
        result = await self.db.execute(
            select(DailyStat).where(
                DailyStat.monitor_id == monitor_id,
                DailyStat.date == date,
            )
        )
        daily_stat = result.scalars().first()
        if not daily_stat:
            return Err(DailyStatNotFound(monitor_id=monitor_id, date=date))
        return Ok(daily_stat)

    @override
    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[DailyStat], AppError]:
        result = await self.db.execute(
            select(DailyStat).where(DailyStat.monitor_id == monitor_id)
        )
        return Ok(list(result.scalars().all()))
