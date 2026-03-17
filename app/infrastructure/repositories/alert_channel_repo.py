import uuid
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AlertChannelNotFoundError, AppError, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import AlertChannelRepository
from app.models.alert_channel import AlertChannel


class SQLAlchemyAlertChannelRepository(AlertChannelRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, channel: AlertChannel) -> Result[AlertChannel, AppError]:
        self.db.add(channel)

        try:
            await self.db.commit()
            await self.db.refresh(channel)
            return Ok(channel)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_id(self, channel_id: uuid.UUID) -> Result[AlertChannel, AppError]:
        query = select(AlertChannel).where(
            AlertChannel.id == channel_id, AlertChannel.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        channel = result.scalars().first()
        if not channel:
            return Err(AlertChannelNotFoundError(channel_id=channel_id))
        return Ok(channel)

    @override
    async def get_all_by_user(
        self, user_id: uuid.UUID
    ) -> Result[list[AlertChannel], AppError]:
        query = select(AlertChannel).where(
            AlertChannel.user_id == user_id, AlertChannel.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return Ok(list(result.scalars().all()))
