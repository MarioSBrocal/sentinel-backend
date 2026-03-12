import uuid
from datetime import datetime

from app.core.errors import AppError, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import PingLogRepository
from app.models.ping_log import PingLog


class PingLogService:
    def __init__(self, ping_log_repo: PingLogRepository):
        self.ping_log_repo = ping_log_repo

    async def create_ping_log(
        self,
        monitor_id: uuid.UUID,
        timestamp: datetime,
        response_time_ms: int,
        is_up: bool,
        status_code: int | None = None,
    ) -> Result[PingLog, AppError]:
        """Record a new ping log entry for a monitor."""
        new_log = PingLog(
            monitor_id=monitor_id,
            timestamp=timestamp,
            response_time_ms=response_time_ms,
            status_code=status_code,
            is_up=is_up,
        )

        try:
            saved_log = await self.ping_log_repo.create(new_log)
            return Ok(saved_log)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_monitor_ping_logs(
        self, monitor_id: uuid.UUID
    ) -> Result[list[PingLog], AppError]:
        """Retrieve all ping logs for a specific monitor."""
        try:
            logs = await self.ping_log_repo.get_all_by_monitor(monitor_id)
            return Ok(logs)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
