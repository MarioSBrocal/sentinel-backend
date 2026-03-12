import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_ping_log_service
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.ping_log import PingLogCreate, PingLogResponse
from app.services.ping_log_service import PingLogService

router = APIRouter(
    tags=["ping_logs"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post("/", response_model=PingLogResponse, status_code=status.HTTP_201_CREATED)
async def create_ping_log(
    ping_log_in: PingLogCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: PingLogService = Depends(get_ping_log_service),  # noqa: B008
):
    """Creates a new ping log for the authenticated user."""

    result = await service.create_ping_log(
        monitor_id=ping_log_in.monitor_id,
        timestamp=ping_log_in.timestamp,
        response_time_ms=ping_log_in.response_time_ms,
        status_code=ping_log_in.status_code,
        is_up=ping_log_in.is_up,
    )

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()


@router.get("/{monitor_id}", response_model=list[PingLogResponse])
async def get_monitor_ping_logs(
    monitor_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: PingLogService = Depends(get_ping_log_service),  # noqa: B008
):
    """Retrieves all ping logs for a specific monitor."""

    result = await service.get_monitor_ping_logs(monitor_id)

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()
