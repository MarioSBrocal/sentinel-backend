import uuid
from typing import Protocol

from app.models.alert_channel import AlertChannel
from app.models.monitor import Monitor
from app.models.user import User


class UserRepository(Protocol):
    """User Repository Protocol defines the interface for user data access."""

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(self, user: User) -> User: ...


class MonitorRepository(Protocol):
    """Monitor Repository Protocol defines the interface for monitor data access."""

    async def create(self, monitor: Monitor) -> Monitor: ...

    async def get_by_id(self, monitor_id: uuid.UUID) -> Monitor | None: ...

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Monitor]: ...


class AlertChannelRepository(Protocol):
    """Alert Channel Repository Protocol defines the interface for alert channel data access."""

    async def create(self, channel: AlertChannel) -> AlertChannel: ...

    async def get_by_id(self, channel_id: uuid.UUID) -> AlertChannel | None: ...

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[AlertChannel]: ...
