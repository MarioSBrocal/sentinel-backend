import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_incident_service
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentResponse
from app.services.incident_service import IncidentService

router = APIRouter(
    tags=["incidents"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: IncidentService = Depends(get_incident_service),  # noqa: B008
):
    """Creates a new incident for the authenticated user."""

    result = await service.create_incident(
        monitor_id=incident_in.monitor_id,
        error_type=incident_in.error_type,
        error_details=incident_in.error_details,
    )

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()


@router.get("/{monitor_id}", response_model=list[IncidentResponse])
async def get_monitor_incidents(
    monitor_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: IncidentService = Depends(get_incident_service),  # noqa: B008
):
    """Retrieves all incidents for a specific monitor."""

    result = await service.get_monitor_incidents(monitor_id)

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()
