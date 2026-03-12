import uuid
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import PingLogRepository
from app.models.ping_log import PingLog


class SQLAlchemyPingLogRepository(PingLogRepository):
    """A repository implementation for PingLog entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, log: PingLog) -> PingLog:
        self.db.add(log)
        try:
            await self.db.commit()
            await self.db.refresh(log)
            return log
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
