import uuid
from datetime import datetime

from app.core.errors import AppError
from app.core.result import Err, Ok, Result
from app.domain.repositories import HourlyStatRepository
from app.models.hourly_stat import HourlyStat


class HourlyStatService:
    def __init__(self, hourly_stat_repo: HourlyStatRepository):
        self.hourly_stat_repo = hourly_stat_repo

    async def create_hourly_stat(
        self,
        monitor_id: uuid.UUID,
        hour_timestamp: datetime,
        total_checks: int,
        successful_checks: int,
        avg_response_time_ms: int,
    ) -> Result[HourlyStat, AppError]:
        """Create a new hourly stat entry for a monitor."""

        new_stat = HourlyStat(
            monitor_id=monitor_id,
            hour_timestamp=hour_timestamp,
            total_checks=total_checks,
            successful_checks=successful_checks,
            avg_response_time_ms=avg_response_time_ms,
        )

        result = await self.hourly_stat_repo.create(new_stat)

        if result.is_err():
            return Err(result.unwrap_err())

        return Ok(result.unwrap())

    async def get_by_monitor_and_hour(
        self, monitor_id: uuid.UUID, hour_timestamp: datetime
    ) -> Result[HourlyStat, AppError]:
        """Retrieve a single hourly stat by monitor and hour."""

        result = await self.hourly_stat_repo.get_by_monitor_and_hour(
            monitor_id, hour_timestamp
        )

        if result.is_err():
            return Err(result.unwrap_err())

        return Ok(result.unwrap())

    async def get_monitor_hourly_stats(
        self, monitor_id: uuid.UUID
    ) -> Result[list[HourlyStat], AppError]:
        """Retrieve all hourly stats for a specific monitor."""

        result = await self.hourly_stat_repo.get_all_by_monitor(monitor_id)

        if result.is_err():
            return Err(result.unwrap_err())

        return Ok(result.unwrap())
