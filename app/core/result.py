from dataclasses import dataclass
from typing import Any, TypeVar

from app.core.errors import AppError

T = TypeVar("T", covariant=True)
E = TypeVar("E", bound=AppError, covariant=True)


@dataclass(frozen=True)
class Ok[T]:
    """Represents a succesful outcome of an operation.

    Attributes
    ----------
    value: `T`
        The successful result data.
    """

    value: T

    def is_ok(self) -> bool:
        """Returns True if the result is Ok."""
        return True

    def is_err(self) -> bool:
        """Returns True if the result is Err."""
        return False

    def unwrap(self) -> T:
        """Returns the contained value if the result is Ok, otherwise raises an exception."""
        return self.value

    def unwrap_err(self) -> Any:
        """Raises an exception with the contained error message if the result is Err, otherwise raises an exception."""
        raise RuntimeError(f"Called unwrap_err on an Ok value: {self.value}")


@dataclass(frozen=True)
class Err[E]:
    """Represents a failed outcome of an operation.

    Attributes
    ----------
    error: `E`
        The error message or data describing the failure.
    """

    error: E

    def is_ok(self) -> bool:
        """Returns True if the result is Ok."""
        return False

    def is_err(self) -> bool:
        """Returns True if the result is Err."""
        return True

    def unwrap(self) -> Any:
        """Raises an exception with the contained error message."""
        raise RuntimeError(f"Called unwrap on an Err value: {self.error}")

    def unwrap_err(self) -> E:
        """Returns the contained error if the result is Err, otherwise raises an exception."""
        return self.error


# A type alias for a result that can be either Ok or Err.
Result = Ok[T] | Err[E]
