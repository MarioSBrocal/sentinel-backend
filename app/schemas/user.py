import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Common attributes for the user."""

    email: EmailStr


class UserCreate(UserBase):
    """Schema for registering new users."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="The user's password. Must be between 8 and 100 characters.",
    )


class UserResponse(UserBase):
    """Schema for returning user data to the frontend (without the password)."""

    id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
