from fastapi import APIRouter, Depends, HTTPException, status

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
    )

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()


@router.get("/", response_model=list[MonitorResponse])
async def get_monitors(
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: MonitorService = Depends(get_monitor_service),  # noqa: B008
):
    """Retrieves all monitors for the authenticated user."""

    result = await service.get_user_monitors(current_user.id)

    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.message
        )

    return result.unwrap()
