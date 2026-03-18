import uuid

from app.core.errors import AppError
from app.core.result import Err, Ok, Result
from app.domain.repositories import AlertChannelRepository
from app.models.alert_channel import AlertChannel, AlertChannelType


class AlertChannelService:
    def __init__(self, channel_repo: AlertChannelRepository):
        self.channel_repo = channel_repo

    async def create_channel(
        self, user_id: uuid.UUID, type: AlertChannelType, destination: str
    ) -> Result[AlertChannel, AppError]:
        """Create a new alert channel for a user."""

        new_channel = AlertChannel(user_id=user_id, type=type, destination=destination)

        result = await self.channel_repo.create(new_channel)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())

    async def get_user_channels(
        self, user_id: uuid.UUID
    ) -> Result[list[AlertChannel], AppError]:
        result = await self.channel_repo.get_all_by_user(user_id)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())
