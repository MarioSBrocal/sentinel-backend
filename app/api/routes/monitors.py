import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_monitor_service
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.monitor import MonitorCreate, MonitorResponse
from app.services.monitor_service import MonitorService

router = APIRouter(
    tags=["monitors"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post("/", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    monitor_in: MonitorCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: MonitorService = Depends(get_monitor_service),  # noqa: B008
):
    """Creates a new monitor for the authenticated user."""

    result = await service.create_monitor(
        user_id=current_user.id,
        name=monitor_in.name,
        url=str(monitor_in.url),
        method=monitor_in.method,
        interval_seconds=monitor_in.interval_seconds,
        headers=monitor_in.headers,
        assertions=monitor_in.assertions,
        body=monitor_in.body,
        organization_id=monitor_in.organization_id,
    )

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()


@router.get("/", response_model=list[MonitorResponse])
async def get_monitors(
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: MonitorService = Depends(get_monitor_service),  # noqa: B008
):
    """Retrieves all monitors for the authenticated user."""

    result = await service.get_user_monitors(current_user.id)

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()


@router.put(
    "/{monitor_id}/alert-channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def add_alert_channel_to_monitor(
    monitor_id: str,
    channel_id: str,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: MonitorService = Depends(get_monitor_service),  # noqa: B008
):
    """Adds an alert channel to a monitor."""

    monitor_id_uuid = uuid.UUID(monitor_id)
    channel_id_uuid = uuid.UUID(channel_id)

    result = await service.link_alert_channel(
        user_id=current_user.id,
        monitor_id=monitor_id_uuid,
        channel_id=channel_id_uuid,
    )

    if result.is_err():
        raise result.unwrap_err()
