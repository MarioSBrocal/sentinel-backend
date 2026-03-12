import uuid
from datetime import datetime

from app.core.errors import AppError, DatabaseError, HourlyStatNotFound
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

        try:
            saved_stat = await self.hourly_stat_repo.create(new_stat)
            return Ok(saved_stat)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_by_monitor_and_hour(
        self, monitor_id: uuid.UUID, hour_timestamp: datetime
    ) -> Result[HourlyStat, AppError]:
        """Retrieve a single hourly stat by monitor and hour."""
        try:
            stat = await self.hourly_stat_repo.get_by_monitor_and_hour(
                monitor_id, hour_timestamp
            )
            if stat is None:
                return Err(
                    HourlyStatNotFound(
                        monitor_id=monitor_id, hour_timestamp=hour_timestamp
                    )
                )

            return Ok(stat)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_monitor_hourly_stats(
        self, monitor_id: uuid.UUID
    ) -> Result[list[HourlyStat], AppError]:
        """Retrieve all hourly stats for a specific monitor."""
        try:
            stats = await self.hourly_stat_repo.get_all_by_monitor(monitor_id)
            return Ok(stats)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
