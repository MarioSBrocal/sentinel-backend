import uuid
from datetime import date, datetime
from typing import Protocol

from app.core.errors import AppError
from app.core.result import Result
from app.models.alert_channel import AlertChannel
from app.models.api_key import ApiKey
from app.models.daily_stat import DailyStat
from app.models.hourly_stat import HourlyStat
from app.models.incident import Incident
from app.models.monitor import Monitor
from app.models.organization import Organization
from app.models.organization_user import OrganizationRole
from app.models.ping_log import PingLog
from app.models.user import User


class ApiKeyRepository(Protocol):
    """API Key Repository Protocol defines the interface for API key data access."""

    async def create(self, api_key: ApiKey) -> Result[ApiKey, AppError]: ...

    async def get_by_user_id(
        self, user_id: uuid.UUID
    ) -> Result[list[ApiKey], AppError]: ...

    async def get_by_hashed_key(self, hashed_key: str) -> Result[ApiKey, AppError]: ...

    async def update_last_used(
        self, api_key_id: uuid.UUID
    ) -> Result[None, AppError]: ...

    async def delete(self, api_key: ApiKey) -> Result[None, AppError]: ...


class UserRepository(Protocol):
    """User Repository Protocol defines the interface for user data access."""

    async def get_by_id(self, user_id: uuid.UUID) -> Result[User, AppError]: ...

    async def get_by_email(self, email: str) -> Result[User, AppError]: ...

    async def create(self, user: User) -> Result[User, AppError]: ...


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

    async def create(self, monitor: Monitor) -> Result[Monitor, AppError]: ...

    async def get_by_id(
        self, monitor_id: uuid.UUID, *, load_channels: bool = False
    ) -> Result[Monitor, AppError]: ...

    async def get_all_active(self) -> Result[list[Monitor], AppError]: ...

    async def get_all_by_user(
        self, user_id: uuid.UUID
    ) -> Result[list[Monitor], AppError]: ...

    async def add_alert_channel(
        self, monitor_id: uuid.UUID, channel: AlertChannel
    ) -> Result[None, AppError]: ...


class AlertChannelRepository(Protocol):
    """Alert Channel Repository Protocol defines the interface for alert channel data access."""

    async def create(self, channel: AlertChannel) -> Result[AlertChannel, AppError]: ...

    async def get_by_id(
        self, channel_id: uuid.UUID
    ) -> Result[AlertChannel, AppError]: ...

    async def get_all_by_user(
        self, user_id: uuid.UUID
    ) -> Result[list[AlertChannel], AppError]: ...


class IncidentRepository(Protocol):
    """Incident Repository Protocol defines the interface for incident data access."""

    async def create(self, incident: Incident) -> Result[Incident, AppError]: ...

    async def get_by_id(self, incident_id: int) -> Result[Incident, AppError]: ...

    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[Incident], AppError]: ...

    async def get_active_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[Incident, AppError]: ...

    async def resolve(self, incident_id: int) -> Result[None, AppError]: ...


class PingLogRepository(Protocol):
    """Ping Log Repository Protocol defines the interface for ping log data access."""

    async def create(self, log: PingLog) -> Result[PingLog, AppError]: ...

    async def get_by_id(self, log_id: int) -> Result[PingLog, AppError]: ...

    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[PingLog], AppError]: ...

    async def ensure_daily_partitions(self) -> Result[None, AppError]: ...

    async def min_date(self) -> Result[date, AppError]: ...

    async def drop_partition_for_date(
        self, partition_date: date
    ) -> Result[None, AppError]: ...


class HourlyStatRepository(Protocol):
    """Hourly Stat Repository Protocol defines the interface for hourly stat data access."""

    async def create(self, stat: HourlyStat) -> Result[HourlyStat, AppError]: ...

    async def get_by_monitor_and_hour(
        self, monitor_id: uuid.UUID, hour_timestamp: datetime
    ) -> Result[HourlyStat, AppError]: ...

    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[HourlyStat], AppError]: ...

    async def max_hour_timestamp(self) -> Result[datetime, AppError]: ...

    async def aggregate_between(
        self,
        start_inclusive: datetime,
        end_exclusive: datetime,
    ) -> Result[int, AppError]: ...


class DailyStatRepository(Protocol):
    """Daily Stat Repository Protocol defines the interface for daily stat data access."""

    async def create(self, stat: DailyStat) -> Result[DailyStat, AppError]: ...

    async def get_by_monitor_and_date(
        self, monitor_id: uuid.UUID, date: date
    ) -> Result[DailyStat, AppError]: ...

    async def get_all_by_monitor(
        self, monitor_id: uuid.UUID
    ) -> Result[list[DailyStat], AppError]: ...

    async def max_date(self) -> Result[date, AppError]: ...

    async def aggregate_between(
        self,
        start_date: date,
        end_date: date,
    ) -> Result[int, AppError]: ...
