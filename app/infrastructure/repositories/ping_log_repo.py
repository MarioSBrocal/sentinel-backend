import uuid
from datetime import UTC, datetime, timedelta
from typing import override

from sqlalchemy import insert, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import PingLogRepository
from app.models.ping_log import PingLog


class SQLAlchemyPingLogRepository(PingLogRepository):
    """A repository implementation for PingLog entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # @override
    # async def create(self, log: PingLog) -> PingLog:
    #     self.db.add(log)
    #     try:
    #         await self.db.commit()
    #         await self.db.refresh(log)
    #         return log
    #     except IntegrityError:
    #         await self.db.rollback()
    #         raise

    @override
    async def create(self, log: PingLog) -> PingLog:
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
                raise Exception("Failed to create PingLog")
            return ping_log
        except IntegrityError:
            await self.db.rollback()
            raise

    @override
    async def get_by_id(self, log_id: int) -> PingLog | None:
        result = await self.db.execute(select(PingLog).where(PingLog.id == log_id))
        return result.scalars().first()

    @override
    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[PingLog]:
        result = await self.db.execute(
            select(PingLog).where(PingLog.monitor_id == monitor_id)
        )
        return list(result.scalars().all())

    @override
    async def ensure_daily_partitions(self) -> None:
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
        except Exception:
            await self.db.rollback()
            raise
