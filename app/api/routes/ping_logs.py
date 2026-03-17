import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_ping_log_service
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.ping_log import PingLogResponse
from app.services.ping_log_service import PingLogService

router = APIRouter(
    tags=["ping_logs"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.get("/{monitor_id}", response_model=list[PingLogResponse])
async def get_monitor_ping_logs(
    monitor_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: PingLogService = Depends(get_ping_log_service),  # noqa: B008
):
    """Retrieves all ping logs for a specific monitor."""

    result = await service.get_monitor_ping_logs(monitor_id)

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()
