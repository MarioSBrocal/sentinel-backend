import uuid
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import AlertChannelRepository
from app.models.alert_channel import AlertChannel


class SQLAlchemyAlertChannelRepository(AlertChannelRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, channel: AlertChannel) -> AlertChannel:
        self.db.add(channel)
        try:
            await self.db.commit()
            await self.db.refresh(channel)
            return channel
        except IntegrityError:
            await self.db.rollback()
            raise

    @override
    async def get_by_id(self, channel_id: uuid.UUID) -> AlertChannel | None:
        query = select(AlertChannel).where(
            AlertChannel.id == channel_id, AlertChannel.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    @override
    async def get_all_by_user(self, user_id: uuid.UUID) -> list[AlertChannel]:
        query = select(AlertChannel).where(
            AlertChannel.user_id == user_id, AlertChannel.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
