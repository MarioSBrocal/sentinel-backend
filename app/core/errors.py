import datetime
import uuid
from dataclasses import dataclass


class AppError(Exception):
    """Base class for all controllable errors in the application.
    It inherits from Exception, so it can be `raised` if necessary.
    """

    @property
    def message(self) -> str:
        """Returns a human-readable error message."""
        return "An unexpected error occurred in the application."


@dataclass
class DatabaseError(AppError):
    detail: str


@dataclass
class UserAlreadyExistsError(AppError):
    """Raised when a user with a given email already exists."""

    email: str

    @property
    def message(self) -> str:
        return f"User with email {self.email} already exists."


@dataclass
class UserNotFoundError(AppError):
    """Raised when a user with a given email is not found."""

    email: str

    @property
    def message(self) -> str:
        return f"User with email {self.email} not found."


@dataclass
class InvalidCredentialsError(AppError):
    """Raised when authentication fails due to invalid credentials."""

    @property
    def message(self) -> str:
        return "Invalid email or password."


@dataclass
class TokenError(AppError):
    """Raised when there is an issue with JWT token validation."""

    @property
    def message(self) -> str:
        return "Invalid or expired token."


@dataclass
class MonitorNotFoundError(AppError):
    """Raised when a monitor with a given ID is not found."""

    monitor_id: uuid.UUID

    @property
    def message(self) -> str:
        return f"Monitor with ID {self.monitor_id} not found."


@dataclass
class AlertChannelNotFoundError(AppError):
    """Raised when an alert channel with a given ID is not found."""

    channel_id: uuid.UUID

    @property
    def message(self) -> str:
        return f"Alert channel with ID {self.channel_id} not found."


@dataclass
class IncidentNotFoundError(AppError):
    """Raised when an incident with a given ID is not found."""

    incident_id: int

    @property
    def message(self) -> str:
        return f"Incident with ID {self.incident_id} not found."


@dataclass
class HourlyStatNotFound(AppError):
    """Raised when an hourly stat with a given monitor ID and hour timestamp is not found."""

    monitor_id: uuid.UUID
    hour_timestamp: datetime.datetime

    @property
    def message(self) -> str:
        return f"Hourly stat for monitor {self.monitor_id} at {self.hour_timestamp} not found."


@dataclass
class DailyStatNotFound(AppError):
    """Raised when a daily stat with a given monitor ID and date is not found."""

    monitor_id: uuid.UUID
    date: datetime.date

    @property
    def message(self) -> str:
        return f"Daily stat for monitor {self.monitor_id} on {self.date} not found."


@dataclass
class UserAlreadyInOrganizationError(AppError):
    """Raised when trying to add a user to an organization they are already a member of."""

    @property
    def message(self) -> str:
        return "User is already a member of the organization."


@dataclass
class UserNotInOrganizationError(AppError):
    """Raised when trying to perform an action on a user that is not a member of the organization."""

    @property
    def message(self) -> str:
        return "User is not a member of the organization."


@dataclass
class OrganizationNotFoundError(AppError):
    """Raised when an organization with a given ID is not found."""

    organization_id: uuid.UUID

    @property
    def message(self) -> str:
        return f"Organization with ID {self.organization_id} not found."
