from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_alert_channel_service, get_current_user
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.alert_channel import AlertChannelCreate, AlertChannelResponse
from app.services.alert_channel_service import AlertChannelService

router = APIRouter(
    tags=["alert-channels"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post(
    "/", response_model=AlertChannelResponse, status_code=status.HTTP_201_CREATED
)
async def create_channel(
    channel_in: AlertChannelCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: AlertChannelService = Depends(get_alert_channel_service),  # noqa: B008
):
    result = await service.create_channel(
        user_id=current_user.id,
        type=channel_in.type,
        destination=channel_in.destination,
    )

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()


@router.get("/", response_model=list[AlertChannelResponse])
async def get_channels(
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: AlertChannelService = Depends(get_alert_channel_service),  # noqa: B008
):
    result = await service.get_user_channels(current_user.id)

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()
