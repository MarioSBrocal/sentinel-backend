import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_hourly_stat_service
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.hourly_stat import HourlyStatCreate, HourlyStatResponse
from app.services.hourly_stat_service import HourlyStatService

router = APIRouter(
    tags=["hourly_stats"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post(
    "/", response_model=HourlyStatResponse, status_code=status.HTTP_201_CREATED
)
async def create_hourly_stat(
    hourly_stat_in: HourlyStatCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: HourlyStatService = Depends(get_hourly_stat_service),  # noqa: B008
):
    """Creates a new hourly stat for the authenticated user."""

    result = await service.create_hourly_stat(
        monitor_id=hourly_stat_in.monitor_id,
        hour_timestamp=hourly_stat_in.hour_timestamp,
        total_checks=hourly_stat_in.total_checks,
        successful_checks=hourly_stat_in.successful_checks,
        avg_response_time_ms=hourly_stat_in.avg_response_time_ms,
    )

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()


@router.get("/{monitor_id}", response_model=list[HourlyStatResponse])
async def get_monitor_hourly_stats(
    monitor_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: HourlyStatService = Depends(get_hourly_stat_service),  # noqa: B008
):
    """Retrieves all hourly stats for a specific monitor."""

    result = await service.get_monitor_hourly_stats(monitor_id)

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()
