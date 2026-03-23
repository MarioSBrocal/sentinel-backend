from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_api_key_service, get_current_user
from app.core.errors import TokenError
from app.models import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse
from app.services.api_key_service import ApiKeyService

router = APIRouter(
    tags=["api-keys"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post(
    "/", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_api_key(
    payload: ApiKeyCreate,
    service: ApiKeyService = Depends(get_api_key_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    result = await service.create_api_key(payload.name, current_user.id)

    if result.is_err():
        raise result.unwrap_err()

    raw_key, new_api_key = result.unwrap()

    return ApiKeyCreateResponse(
        id=new_api_key.id,
        name=new_api_key.name,
        prefix=new_api_key.prefix,
        created_at=new_api_key.created_at,
        last_used_at=new_api_key.last_used_at,
        raw_key=raw_key,
    )


@router.delete("/{hashed_key}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    hashed_key: str,
    service: ApiKeyService = Depends(get_api_key_service),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    result = await service.delete_api_key_by_hash(hashed_key)

    if result.is_err():
        raise result.unwrap_err()
