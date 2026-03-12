# app/services/monitor_service.py
import uuid

from app.core.errors import AppError, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import MonitorRepository
from app.models.monitor import Monitor


class MonitorService:
    def __init__(self, monitor_repo: MonitorRepository):
        self.monitor_repo = monitor_repo

    async def create_monitor(
        self,
        user_id: uuid.UUID,
        name: str,
        url: str,
        method: str,
        interval_seconds: int,
    ) -> Result[Monitor, AppError]:
        """Create a new monitor for a user."""
        new_monitor = Monitor(
            user_id=user_id,
            name=name,
            url=url,
            method=method,
            interval_seconds=interval_seconds,
            is_active=True,
        )

        try:
            saved_monitor = await self.monitor_repo.create(new_monitor)
            return Ok(saved_monitor)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_user_monitors(
        self, user_id: uuid.UUID
    ) -> Result[list[Monitor], AppError]:
        """Retrieve all monitors that belong to a specific user."""
        try:
            monitors = await self.monitor_repo.get_all_by_user(user_id)
            return Ok(monitors)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
