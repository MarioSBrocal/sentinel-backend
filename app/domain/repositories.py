import uuid
from datetime import date, datetime
from typing import Protocol

from app.models.alert_channel import AlertChannel
from app.models.daily_stat import DailyStat
from app.models.hourly_stat import HourlyStat
from app.models.incident import Incident
from app.models.monitor import Monitor
from app.models.ping_log import PingLog
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


class IncidentRepository(Protocol):
    """Incident Repository Protocol defines the interface for incident data access."""

    async def create(self, incident: Incident) -> Incident: ...

    async def get_by_id(self, incident_id: uuid.UUID) -> Incident | None: ...

    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[Incident]: ...


class PingLogRepository(Protocol):
    """Ping Log Repository Protocol defines the interface for ping log data access."""

    async def create(self, log: PingLog) -> PingLog: ...

    async def get_by_id(self, log_id: uuid.UUID) -> PingLog | None: ...

    async def get_all_by_monitor(self, monitor_id: uuid.UUID) -> list[PingLog]: ...


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
