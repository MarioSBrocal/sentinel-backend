import uuid
from datetime import datetime
from typing import override

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, DatabaseError, HourlyStatNotFound
from app.core.result import Err, Ok, Result
from app.domain.repositories import HourlyStatRepository
from app.models.hourly_stat import HourlyStat
from app.models.ping_log import PingLog


class SQLAlchemyHourlyStatRepository(HourlyStatRepository):
    """A repository implementation for HourlyStat entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, stat: HourlyStat) -> Result[HourlyStat, AppError]:
        self.db.add(stat)

        try:
            await self.db.commit()
            await self.db.refresh(stat)
            return Ok(stat)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_monitor_and_hour(
        self, monitor_id: uuid.UUID, hour_timestamp: datetime
    ) -> Result[HourlyStat, AppError]:
        result = await self.db.execute(
            select(HourlyStat).where(
                HourlyStat.monitor_id == monitor_id,
                HourlyStat.hour_timestamp == hour_timestamp,
            )
        )
        stat = result.scalars().first()
        if not stat:
            return Err(
                HourlyStatNotFound(monitor_id=monitor_id, hour_timestamp=hour_timestamp)
            )
        return Ok(stat)

    @override
    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[HourlyStat], AppError]:
        result = await self.db.execute(
            select(HourlyStat).where(HourlyStat.monitor_id == monitor_id)
        )
        return Ok(list(result.scalars().all()))

    @override
    async def max_hour_timestamp(self) -> Result[datetime, AppError]:
        result = await self.db.execute(select(func.max(HourlyStat.hour_timestamp)))
        max_timestamp = result.scalars().first()
        if max_timestamp is None:
            return Ok(datetime.min)
        return Ok(max_timestamp)

    @override
    async def aggregate_between(
        self,
        start_inclusive: datetime,
        end_exclusive: datetime,
    ) -> Result[int, AppError]:
        hour_bucket = func.date_trunc("hour", PingLog.timestamp).label("hour_timestamp")

        aggregation_query = (
            select(
                PingLog.monitor_id,
                hour_bucket,
                func.avg(PingLog.response_time_ms).label("avg_response_time_ms"),
                func.count(PingLog.id)
                .filter(PingLog.is_up.is_(True))
                .label("successful_checks"),
                func.count(PingLog.id).label("total_checks"),
            )
            .where(
                PingLog.timestamp >= start_inclusive,
                PingLog.timestamp < end_exclusive,
            )
            .group_by(PingLog.monitor_id, hour_bucket)
        )

        try:
            result = await self.db.execute(aggregation_query)
            rows = result.all()

            if not rows:
                return Ok(0)

            insert_data = [
                {
                    "monitor_id": row.monitor_id,
                    "hour_timestamp": row.hour_timestamp,
                    "total_checks": row.total_checks,
                    "successful_checks": row.successful_checks,
                    "avg_response_time_ms": row.avg_response_time_ms,
                }
                for row in rows
            ]

            insert_stmt = insert(HourlyStat).values(insert_data)
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[HourlyStat.monitor_id, HourlyStat.hour_timestamp],
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
