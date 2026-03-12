import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_daily_stat_service
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.daily_stat import DailyStatCreate, DailyStatResponse
from app.services.daily_stat_service import DailyStatService

router = APIRouter(
    tags=["daily_stats"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post("/", response_model=DailyStatResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_stat(
    daily_stat_in: DailyStatCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: DailyStatService = Depends(get_daily_stat_service),  # noqa: B008
):
    """Creates a new daily stat for the authenticated user."""

    result = await service.create_daily_stat(
        monitor_id=daily_stat_in.monitor_id,
        date=daily_stat_in.date,
        total_checks=daily_stat_in.total_checks,
        successful_checks=daily_stat_in.successful_checks,
        avg_response_time_ms=daily_stat_in.avg_response_time_ms,
    )

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()


@router.get("/{monitor_id}", response_model=list[DailyStatResponse])
async def get_monitor_daily_stats(
    monitor_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: DailyStatService = Depends(get_daily_stat_service),  # noqa: B008
):
    """Retrieves all daily stats for a specific monitor."""

    result = await service.get_monitor_daily_stats(monitor_id)

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()
