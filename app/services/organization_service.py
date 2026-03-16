import uuid

from app.core.errors import (
    AppError,
)
from app.core.result import Err, Ok, Result
from app.domain.repositories import OrganizationRepository
from app.models.organization import Organization
from app.models.organization_user import OrganizationRole


class OrganizationService:
    def __init__(self, organization_repo: OrganizationRepository):
        self.organization_repo: OrganizationRepository = organization_repo

    async def create_organization(
        self, name: str, user_id: uuid.UUID
    ) -> Result[Organization, AppError]:
        """Create a new organization with the given name and add the user as the owner."""

        new_organization = Organization(name=name)

        result_create = await self.organization_repo.create(new_organization)
        if result_create.is_err():
            return Err(result_create.unwrap_err())
        organization = result_create.unwrap()

        result_add_user = await self.organization_repo.add_user(
            organization.id, user_id, OrganizationRole.OWNER
        )
        if result_add_user.is_err():
            return Err(result_add_user.unwrap_err())
        return Ok(organization)

    async def get_organization_by_id(
        self, organization_id: uuid.UUID
    ) -> Result[Organization, AppError]:
        result = await self.organization_repo.get_by_id(organization_id)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())

    async def update_organization(
        self, organization_id: uuid.UUID, *, name: str | None = None
    ) -> Result[None, AppError]:
        result = await self.organization_repo.update(organization_id, name=name)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())

    async def delete_organization(
        self, organization_id: uuid.UUID
    ) -> Result[None, AppError]:
        result = await self.organization_repo.delete(organization_id)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())

    async def add_user_to_organization(
        self, organization_id: uuid.UUID, user_id: uuid.UUID, role: OrganizationRole
    ) -> Result[None, AppError]:
        result = await self.organization_repo.add_user(organization_id, user_id, role)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())

    async def remove_user_from_organization(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> Result[None, AppError]:
        result = await self.organization_repo.remove_user(organization_id, user_id)
        if result.is_err():
            return Err(result.unwrap_err())
        return Ok(result.unwrap())
