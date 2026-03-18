import datetime
import uuid
from dataclasses import dataclass

from fastapi import status


class AppError(Exception):
    """Base class for all controllable errors in the application.
    It inherits from Exception, so it can be `raised` if necessary.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    @property
    def message(self) -> str:
        """Returns a human-readable error message."""
        return "An unexpected error occurred in the application."


@dataclass
class DatabaseError(AppError):
    """Raised when there is a database-related error."""

    detail: str


# ApiKey-related errors
@dataclass
class ApiKeyNotFoundError(AppError):
    """Raised when an API key with a given hash is not found."""

    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return "API key not found."


# User-related errors
@dataclass
class UserAlreadyExistsError(AppError):
    """Raised when a user with a given email already exists."""

    email: str
    status_code: int = status.HTTP_400_BAD_REQUEST

    @property
    def message(self) -> str:
        return f"User with email {self.email} already exists."


@dataclass
class UserNotFoundError(AppError):
    """Raised when a user with a given email is not found."""

    user_id: uuid.UUID | None = None
    email: str | None = None
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return (
            f"User with email {self.email} not found."
            if self.email
            else f"User with ID {self.user_id} not found."
        )


@dataclass
class InvalidCredentialsError(AppError):
    """Raised when authentication fails due to invalid credentials."""

    status_code: int = status.HTTP_401_UNAUTHORIZED

    @property
    def message(self) -> str:
        return "Invalid email or password."


@dataclass
class TokenError(AppError):
    """Raised when there is an issue with JWT token validation."""

    status_code: int = status.HTTP_401_UNAUTHORIZED

    @property
    def message(self) -> str:
        return "Invalid or expired token."


# Organization-related errors
@dataclass
class OrganizationNotFoundError(AppError):
    """Raised when an organization with a given ID is not found."""

    organization_id: uuid.UUID
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return f"Organization with ID {self.organization_id} not found."


@dataclass
class UserAlreadyInOrganizationError(AppError):
    """Raised when trying to add a user to an organization they are already a member of."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    @property
    def message(self) -> str:
        return "User is already a member of the organization."


@dataclass
class UserNotInOrganizationError(AppError):
    """Raised when trying to perform an action on a user that is not a member of the organization."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    @property
    def message(self) -> str:
        return "User is not a member of the organization."


# Monitor-related errors
@dataclass
class MonitorNotFoundError(AppError):
    """Raised when a monitor with a given ID is not found."""

    monitor_id: uuid.UUID
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return f"Monitor with ID {self.monitor_id} not found."


@dataclass
class AlertChannelAlreadyLinkedError(AppError):
    """Raised when trying to link an alert channel to a monitor it's already linked to."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    @property
    def message(self) -> str:
        return "Alert channel is already linked to the monitor."


# Alertchannel-related errors
@dataclass
class AlertChannelNotFoundError(AppError):
    """Raised when an alert channel with a given ID is not found."""

    channel_id: uuid.UUID
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return f"Alert channel with ID {self.channel_id} not found."


# Incident-related errors
@dataclass
class IncidentNotFoundError(AppError):
    """Raised when an incident with a given ID is not found."""

    incident_id: int | None = None
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return (
            f"Incident with ID {self.incident_id} not found."
            if self.incident_id
            else "No active incident found for the monitor."
        )


# PingLog-related errors
@dataclass
class PingLogNotFoundError(AppError):
    """Raised when a ping log with a given ID is not found."""

    log_id: int
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return f"Ping log with ID {self.log_id} not found."


# HourlyStat-related errors
@dataclass
class HourlyStatNotFound(AppError):
    """Raised when an hourly stat with a given monitor ID and hour timestamp is not found."""

    monitor_id: uuid.UUID
    hour_timestamp: datetime.datetime
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return f"Hourly stat for monitor {self.monitor_id} at {self.hour_timestamp} not found."


# DailyStat-related errors
@dataclass
class DailyStatNotFound(AppError):
    """Raised when a daily stat with a given monitor ID and date is not found."""

    monitor_id: uuid.UUID
    date: datetime.date
    status_code: int = status.HTTP_404_NOT_FOUND

    @property
    def message(self) -> str:
        return f"Daily stat for monitor {self.monitor_id} on {self.date} not found."
