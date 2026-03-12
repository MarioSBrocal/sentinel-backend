import uuid
from datetime import date

from app.core.errors import AppError, DailyStatNotFound, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import DailyStatRepository
from app.models.daily_stat import DailyStat


class DailyStatService:
    def __init__(self, daily_stat_repo: DailyStatRepository):
        self.daily_stat_repo = daily_stat_repo

    async def create_daily_stat(
        self,
        monitor_id: uuid.UUID,
        date: date,
        total_checks: int,
        successful_checks: int,
        avg_response_time_ms: int,
    ) -> Result[DailyStat, AppError]:
        """Create a new daily stat entry for a monitor."""
        new_stat = DailyStat(
            monitor_id=monitor_id,
            date=date,
            total_checks=total_checks,
            successful_checks=successful_checks,
            avg_response_time_ms=avg_response_time_ms,
        )

        try:
            saved_stat = await self.daily_stat_repo.create(new_stat)
            return Ok(saved_stat)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_by_monitor_and_date(
        self, monitor_id: uuid.UUID, date: date
    ) -> Result[DailyStat, AppError]:
        """Retrieve a single daily stat by monitor and date."""
        try:
            stat = await self.daily_stat_repo.get_by_monitor_and_date(monitor_id, date)
            if stat is None:
                return Err(DailyStatNotFound(monitor_id=monitor_id, date=date))

            return Ok(stat)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def get_monitor_daily_stats(
        self, monitor_id: uuid.UUID
    ) -> Result[list[DailyStat], AppError]:
        """Retrieve all daily stats for a specific monitor."""
        try:
            stats = await self.daily_stat_repo.get_all_by_monitor(monitor_id)
            return Ok(stats)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))
