import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_organization_service
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    UpdateUserRoleRequest,
)
from app.services.organization_service import OrganizationService

router = APIRouter(
    tags=["users"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.post(
    "/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED
)
async def create_organization(
    organization_in: OrganizationCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: OrganizationService = Depends(get_organization_service),  # noqa: B008
):
    """Creates a new organization for the authenticated user."""

    result = await service.create_organization(organization_in.name, current_user.id)

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: OrganizationService = Depends(get_organization_service),  # noqa: B008
):
    """Retrieves an organization by its ID."""

    result = await service.get_organization_by_id(organization_id)

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()


@router.patch("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_organization(
    organization_id: uuid.UUID,
    organization_in: OrganizationCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: OrganizationService = Depends(get_organization_service),  # noqa: B008
):
    """Updates an organization's details."""

    result = await service.update_organization(
        organization_id, name=organization_in.name
    )

    if result.is_err():
        raise result.unwrap_err()


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: OrganizationService = Depends(get_organization_service),  # noqa: B008
):
    """Deletes an organization."""

    result = await service.delete_organization(organization_id)

    if result.is_err():
        raise result.unwrap_err()


@router.put(
    "/{organization_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def add_user_to_organization(
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    update_request: UpdateUserRoleRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: OrganizationService = Depends(get_organization_service),  # noqa: B008
):
    """Adds a user to an organization."""

    result = await service.add_user_to_organization(
        organization_id, user_id, update_request.role
    )

    if result.is_err():
        raise result.unwrap_err()


@router.delete(
    "/{organization_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_user_from_organization(
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: OrganizationService = Depends(get_organization_service),  # noqa: B008
):
    """Removes a user from an organization."""

    result = await service.remove_user_from_organization(organization_id, user_id)

    if result.is_err():
        raise result.unwrap_err()
