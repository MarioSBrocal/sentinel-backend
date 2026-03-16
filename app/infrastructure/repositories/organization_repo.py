import uuid
from datetime import UTC, datetime
from typing import override

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    AppError,
    DatabaseError,
    OrganizationNotFoundError,
    UserAlreadyInOrganizationError,
    UserNotInOrganizationError,
)
from app.core.result import Err, Ok, Result
from app.domain.repositories import OrganizationRepository
from app.models.organization import Organization
from app.models.organization_user import OrganizationRole, OrganizationUser


class SQLAlchemyOrganizationRepository(OrganizationRepository):
    """A repository implementation for Organization entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(
        self, organization: Organization
    ) -> Result[Organization, AppError]:
        self.db.add(organization)
        try:
            await self.db.commit()
            await self.db.refresh(organization)
            return Ok(organization)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_id(
        self, organization_id: uuid.UUID
    ) -> Result[Organization, AppError]:
        result = await self.db.execute(
            select(Organization).where(
                Organization.id == organization_id, Organization.deleted_at.is_(None)
            )
        )
        organization = result.scalars().first()
        if not organization:
            return Err(OrganizationNotFoundError(organization_id=organization_id))
        return Ok(organization)

    @override
    async def update(
        self,
        organization_id: uuid.UUID,
        *,
        name: str | None = None,
    ) -> Result[None, AppError]:
        result = await self.get_by_id(organization_id)
        if result.is_err():
            return Err(result.unwrap_err())

        organization = result.unwrap()
        if name is not None:
            organization.name = name

        try:
            await self.db.commit()
            return Ok(None)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def delete(self, organization_id: uuid.UUID) -> Result[None, AppError]:
        result = await self.get_by_id(organization_id)
        if result.is_err():
            return Err(result.unwrap_err())

        organization = result.unwrap()
        organization.deleted_at = datetime.now(UTC)

        try:
            await self.db.commit()
            return Ok(None)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def has_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> Result[bool, AppError]:
        result = await self.db.execute(
            select(
                exists().where(
                    OrganizationUser.organization_id == organization_id,
                    OrganizationUser.user_id == user_id,
                )
            )
        )
        result = result.scalar()
        if result is None:
            return Err(
                DatabaseError(
                    detail="Failed to check user membership due to database error."
                )
            )
        return Ok(result)

    @override
    async def add_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID, role: OrganizationRole
    ) -> Result[None, AppError]:
        new_member = OrganizationUser(
            organization_id=organization_id, user_id=user_id, role=role
        )
        self.db.add(new_member)

        try:
            await self.db.commit()
            return Ok(None)
        except IntegrityError as e:
            await self.db.rollback()
            if (
                hasattr(e.orig, "pgcode")
                and e.orig.pgcode == "23505"  # Unique violation
            ):
                return Err(UserAlreadyInOrganizationError())
            return Err(DatabaseError(detail=str(e)))

    @override
    async def remove_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> Result[None, AppError]:
        result = await self.db.execute(
            select(OrganizationUser).where(
                OrganizationUser.organization_id == organization_id,
                OrganizationUser.user_id == user_id,
            )
        )
        membership = result.scalars().first()
        if not membership:
            return Err(UserNotInOrganizationError())

        await self.db.delete(membership)
        try:
            await self.db.commit()
            return Ok(None)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))
