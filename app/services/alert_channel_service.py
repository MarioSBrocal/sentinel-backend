import uuid

from app.core.errors import AppError, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import AlertChannelRepository
from app.models.alert_channel import AlertChannel, AlertChannelType


class AlertChannelService:
    def __init__(self, channel_repo: AlertChannelRepository):
        self.channel_repo = channel_repo

    async def create_channel(
        self, user_id: uuid.UUID, name: str, type: AlertChannelType, destination: str
    ) -> Result[AlertChannel, AppError]:
        """Create a new alert channel for a user."""

        new_channel = AlertChannel(
            user_id=user_id, name=name, type=type, destination=destination
        )

        try:
            saved_channel = await self.channel_repo.create(new_channel)
            return Ok(saved_channel)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_user_channels(
        self, user_id: uuid.UUID
    ) -> Result[list[AlertChannel], AppError]:
        try:
            channels = await self.channel_repo.get_all_by_user(user_id)
            return Ok(channels)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
