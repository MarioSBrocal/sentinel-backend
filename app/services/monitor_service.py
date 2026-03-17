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
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Result[Monitor, AppError]:
        """Create a new monitor for a user."""

        new_monitor = Monitor(
            user_id=user_id if organization_id is None else None,
            organization_id=organization_id,
            name=name,
            url=url,
            method=method,
            interval_seconds=interval_seconds,
            is_paused=False,
            headers=headers,
            assertions=[assertion.model_dump(mode="json") for assertion in assertions],
            body=body,
        )

        result = await self.monitor_repo.create(new_monitor)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())

    async def get_user_monitors(
        self, user_id: uuid.UUID
    ) -> Result[list[Monitor], AppError]:
        """Retrieve all monitors that belong to a specific user."""

        result = await self.monitor_repo.get_all_by_user(user_id)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())

    async def link_alert_channel(
        self, monitor_id: uuid.UUID, channel_id: uuid.UUID, user_id: uuid.UUID
    ) -> Result[None, AppError]:
        monitor_result = await self.monitor_repo.get_by_id(monitor_id)
        if monitor_result.is_err():
            return Err(monitor_result.unwrap_err())
        monitor = monitor_result.unwrap()
        if monitor.user_id != user_id:
            return Err(MonitorNotFoundError(monitor_id=monitor_id))

        channel_result = await self.channel_repo.get_by_id(channel_id)
        if channel_result.is_err():
            return Err(channel_result.unwrap_err())
        channel = channel_result.unwrap()
        if channel.user_id != user_id:
            return Err(AlertChannelNotFoundError(channel_id=channel_id))

        try:
            await self.monitor_repo.add_alert_channel(monitor_id, channel)
            return Ok(None)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
