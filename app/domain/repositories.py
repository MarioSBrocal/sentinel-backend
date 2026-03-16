import uuid
from datetime import date, datetime
from typing import Protocol

from app.core.errors import AppError
from app.core.result import Result
from app.models.alert_channel import AlertChannel
from app.models.daily_stat import DailyStat
from app.models.hourly_stat import HourlyStat
from app.models.incident import Incident
from app.models.monitor import Monitor
from app.models.organization import Organization
from app.models.organization_user import OrganizationRole
from app.models.ping_log import PingLog
from app.models.user import User


class UserRepository(Protocol):
    """User Repository Protocol defines the interface for user data access."""

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(self, user: User) -> User: ...


class OrganizationRepository(Protocol):
    """Organization Repository Protocol defines the interface for organization data access."""

    async def create(
        self, organization: Organization
    ) -> Result[Organization, AppError]: ...

    async def get_by_id(
        self, organization_id: uuid.UUID
    ) -> Result[Organization, AppError]: ...

    async def update(
        self,
        organization_id: uuid.UUID,
        *,
        name: str | None = None,
    ) -> Result[None, AppError]: ...

    async def delete(self, organization_id: uuid.UUID) -> Result[None, AppError]: ...

    async def has_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> Result[bool, AppError]: ...

    async def add_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID, role: OrganizationRole
    ) -> Result[None, AppError]: ...

    async def remove_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> Result[None, AppError]: ...


class MonitorRepository(Protocol):
    """Monitor Repository Protocol defines the interface for monitor data access."""

    async def create(self, monitor: Monitor) -> Monitor: ...

    async def get_by_id(self, monitor_id: uuid.UUID) -> Monitor | None: ...

    async def get_by_id_with_channels(
        self, monitor_id: uuid.UUID
    ) -> Monitor | None: ...

    async def get_all_active(self) -> list[Monitor]: ...

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Monitor]: ...

    async def add_alert_channel(
        self, monitor_id: uuid.UUID, channel: AlertChannel
    ) -> None: ...


class AlertChannelRepository(Protocol):
    """Alert Channel Repository Protocol defines the interface for alert channel data access."""

    async def create(self, channel: AlertChannel) -> AlertChannel: ...

    async def get_by_id(self, channel_id: uuid.UUID) -> AlertChannel | None: ...

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[AlertChannel]: ...


class IncidentRepository(Protocol):
    """Incident Repository Protocol defines the interface for incident data access."""

    async def create(self, incident: Incident) -> Incident: ...

    async def get_by_id(self, incident_id: int) -> Incident | None: ...

    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[Incident]: ...

    async def get_active_by_monitor(self, monitor_id: uuid.UUID) -> Incident | None: ...

    async def resolve(self, incident_id: int) -> None: ...


class PingLogRepository(Protocol):
    """Ping Log Repository Protocol defines the interface for ping log data access."""

    async def create(self, log: PingLog) -> PingLog: ...

    async def get_by_id(self, log_id: int) -> PingLog | None: ...

    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[PingLog]: ...

    async def ensure_daily_partitions(self) -> None: ...


class HourlyStatRepository(Protocol):
    """Hourly Stat Repository Protocol defines the interface for hourly stat data access."""

    async def create(self, stat: HourlyStat) -> HourlyStat: ...

    async def get_by_monitor_and_hour(
        self, monitor_id: uuid.UUID, hour_timestamp: datetime
    ) -> HourlyStat | None: ...

    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[HourlyStat]: ...


class DailyStatRepository(Protocol):
    """Daily Stat Repository Protocol defines the interface for daily stat data access."""

    async def create(self, stat: DailyStat) -> DailyStat: ...

    async def get_by_monitor_and_date(
        self, monitor_id: uuid.UUID, date: date
    ) -> DailyStat | None: ...

    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[DailyStat]: ...
