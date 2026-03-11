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
