import uuid
from datetime import UTC, date, datetime, timedelta
from typing import override

from sqlalchemy import func, insert, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, DatabaseError, PingLogNotFoundError
from app.core.result import Err, Ok, Result
from app.domain.repositories import PingLogRepository
from app.models.ping_log import PingLog


class SQLAlchemyPingLogRepository(PingLogRepository):
    """A repository implementation for PingLog entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, log: PingLog) -> Result[PingLog, AppError]:
        stmt = (
            insert(PingLog)
            .values(
                monitor_id=log.monitor_id,
                timestamp=log.timestamp,
                status_code=log.status_code,
                response_time_ms=log.response_time_ms,
                is_up=log.is_up,
            )
            .returning(PingLog)
        )

        try:
            result = await self.db.execute(stmt)
            await self.db.commit()
            ping_log = result.scalars().first()
            if ping_log is None:
                return Err(DatabaseError("Failed to create PingLog"))
            return Ok(ping_log)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_id(self, log_id: int) -> Result[PingLog, AppError]:
        result = await self.db.execute(select(PingLog).where(PingLog.id == log_id))
        ping_log = result.scalars().first()
        if ping_log is None:
            return Err(PingLogNotFoundError(log_id=log_id))
        return Ok(ping_log)

    @override
    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[PingLog], AppError]:
        result = await self.db.execute(
            select(PingLog).where(PingLog.monitor_id == monitor_id)
        )
        return Ok(list(result.scalars().all()))

    @override
    async def ensure_daily_partitions(self) -> Result[None, AppError]:
        """
        Ensures that daily partitions for the ping_logs table exist for today and tomorrow.
        This method should be called at least once a day to maintain the partitioning strategy.
        """

        today = datetime.now(UTC).date()
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)

        today_table = f"ping_logs_{today.strftime('%Y_%m_%d')}"
        tomorrow_table = f"ping_logs_{tomorrow.strftime('%Y_%m_%d')}"

        sql_today = text(f"""
            CREATE TABLE IF NOT EXISTS {today_table} 
            PARTITION OF ping_logs 
            FOR VALUES FROM ('{today.strftime("%Y-%m-%d")} 00:00:00') 
            TO ('{tomorrow.strftime("%Y-%m-%d")} 00:00:00');
        """)

        sql_tomorrow = text(f"""
            CREATE TABLE IF NOT EXISTS {tomorrow_table} 
            PARTITION OF ping_logs 
            FOR VALUES FROM ('{tomorrow.strftime("%Y-%m-%d")} 00:00:00') 
            TO ('{day_after.strftime("%Y-%m-%d")} 00:00:00');
        """)

        try:
            await self.db.execute(sql_today)
            await self.db.execute(sql_tomorrow)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))
        return Ok(None)

    @override
    async def min_date(self) -> Result[date, AppError]:
        result = await self.db.execute(select(func.min(PingLog.timestamp)))
        min_timestamp = result.scalars().first()
        if min_timestamp is None:
            return Ok(date.today())
        return Ok(min_timestamp.date())

    @override
    async def drop_partition_for_date(
        self, partition_date: date
    ) -> Result[None, AppError]:
        partition_table = f"ping_logs_{partition_date.strftime('%Y_%m_%d')}"
        sql_drop = text(f"DROP TABLE IF EXISTS {partition_table};")

        try:
            await self.db.execute(sql_drop)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))
        return Ok(None)
