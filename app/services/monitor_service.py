import uuid
from typing import Any

from app.core.errors import (
    AlertChannelNotFoundError,
    AppError,
    DatabaseError,
    MonitorNotFoundError,
)
from app.core.result import Err, Ok, Result
from app.domain.repositories import AlertChannelRepository, MonitorRepository
from app.models.monitor import Monitor
from app.schemas.monitor import Assertion


class MonitorService:
    def __init__(
        self, monitor_repo: MonitorRepository, channel_repo: AlertChannelRepository
    ):
        self.monitor_repo = monitor_repo
        self.channel_repo = channel_repo

    async def create_monitor(
        self,
        user_id: uuid.UUID,
        name: str,
        url: str,
        method: str,
        interval_seconds: int,
        headers: dict[str, Any],
        assertions: list[Assertion],
        body: dict[str, Any] | None = None,
    ) -> Result[Monitor, AppError]:
        """Create a new monitor for a user."""
        new_monitor = Monitor(
            user_id=user_id,
            name=name,
            url=url,
            method=method,
            interval_seconds=interval_seconds,
            is_paused=False,
            headers=headers,
            assertions=[assertion.model_dump(mode="json") for assertion in assertions],
            body=body,
        )

        try:
            saved_monitor = await self.monitor_repo.create(new_monitor)
            return Ok(saved_monitor)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_user_monitors(
        self, user_id: uuid.UUID
    ) -> Result[list[Monitor], AppError]:
        """Retrieve all monitors that belong to a specific user."""
        try:
            monitors = await self.monitor_repo.get_all_by_user(user_id)
            return Ok(monitors)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def link_alert_channel(
        self, monitor_id: uuid.UUID, channel_id: uuid.UUID, user_id: uuid.UUID
    ) -> Result[None, AppError]:
        monitor = await self.monitor_repo.get_by_id(monitor_id)
        if not monitor or monitor.user_id != user_id:
            return Err(MonitorNotFoundError(monitor_id=monitor_id))

        channel = await self.channel_repo.get_by_id(channel_id)
        if not channel or channel.user_id != user_id:
            return Err(AlertChannelNotFoundError(channel_id=channel_id))

        try:
            await self.monitor_repo.add_alert_channel(monitor_id, channel)
            return Ok(None)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
