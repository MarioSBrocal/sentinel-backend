import uuid
from typing import Protocol

from app.models.monitor import Monitor
from app.models.user import User


class UserRepository(Protocol):
    """User Repository Protocol defines the interface for user data access."""

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(self, user: User) -> User: ...


class MonitorRepository(Protocol):
    """Monitor Repository Protocol defines the interface for monitor data access."""

    async def create(self, monitor: Monitor) -> Monitor:
        """Guarda un nuevo monitor."""
        ...

    async def get_by_id(self, monitor_id: uuid.UUID) -> Monitor | None:
        """Busca un monitor por su ID."""
        ...

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Monitor]:
        """Devuelve todos los monitores que pertenecen a un usuario específico."""
        ...
