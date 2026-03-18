import uuid
from datetime import date, datetime, time
from typing import override

from sqlalchemy import Date, cast, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, DailyStatNotFound, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import DailyStatRepository
from app.models.daily_stat import DailyStat
from app.models.ping_log import PingLog


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

    @override
    async def max_date(self) -> Result[date, AppError]:
        result = await self.db.execute(select(func.max(DailyStat.date)))
        max_date = result.scalars().first()
        if max_date is None:
            return Ok(date.min)
        return Ok(max_date)

    @override
    async def aggregate_between(
        self, start_date: date, end_date: date
    ) -> Result[int, AppError]:
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.min)

        day_bucket = cast(func.date_trunc("day", PingLog.timestamp), Date).label("date")

        aggregation_query = (
            select(
                PingLog.monitor_id,
                day_bucket,
                func.avg(PingLog.response_time_ms).label("avg_response_time_ms"),
                func.count(PingLog.id)
                .filter(PingLog.is_up.is_(True))
                .label("successful_checks"),
                func.count(PingLog.id).label("total_checks"),
            )
            .where(
                PingLog.timestamp >= start_dt,
                PingLog.timestamp < end_dt,
            )
            .group_by(PingLog.monitor_id, day_bucket)
        )

        try:
            result = await self.db.execute(aggregation_query)
            rows = result.all()

            if not rows:
                return Ok(0)

            insert_data = [
                {
                    "monitor_id": row.monitor_id,
                    "date": row.date,
                    "total_checks": row.total_checks,
                    "successful_checks": row.successful_checks,
                    "avg_response_time_ms": int(row.avg_response_time_ms),
                }
                for row in rows
            ]

            insert_stmt = insert(DailyStat).values(insert_data)
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[DailyStat.monitor_id, DailyStat.date],
                set_={
                    "total_checks": insert_stmt.excluded.total_checks,
                    "successful_checks": insert_stmt.excluded.successful_checks,
                    "avg_response_time_ms": insert_stmt.excluded.avg_response_time_ms,
                },
            )

            await self.db.execute(upsert_stmt)
            await self.db.commit()
            return Ok(len(insert_data))
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))
