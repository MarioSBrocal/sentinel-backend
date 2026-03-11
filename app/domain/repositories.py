from typing import Protocol

from app.models.user import User


class UserRepository(Protocol):
    """User Repository Protocol defines the interface for user data access."""

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(self, user: User) -> User: ...
