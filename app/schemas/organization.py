import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.organization_user import OrganizationRole


class OrganizationBase(BaseModel):
    """Common attributes for the organization."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="The organization's name. Must be between 2 and 100 characters.",
    )


class OrganizationCreate(OrganizationBase):
    """Schema for creating new organizations."""

    pass


class OrganizationResponse(OrganizationBase):
    """Schema for returning organization details."""

    id: uuid.UUID = Field(..., description="The unique identifier of the organization.")
    created_at: datetime = Field(
        ..., description="The timestamp when the organization was created."
    )

    model_config = ConfigDict(from_attributes=True)


class UpdateUserRoleRequest(BaseModel):
    """Schema for updating a user's role within an organization."""

    role: OrganizationRole = Field(
        ..., description="The new role to assign to the user."
    )
