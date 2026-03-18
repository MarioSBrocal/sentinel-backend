from pydantic import BaseModel


class Token(BaseModel):
    """Schema for the JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Schema for the token refresh request."""

    refresh_token: str


class TokenData(BaseModel):
    """Schema for the data contained in the JWT token."""

    email: str | None = None
