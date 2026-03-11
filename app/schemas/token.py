from pydantic import BaseModel


class Token(BaseModel):
    """Schema for the JWT token response."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for the data contained in the JWT token."""

    email: str | None = None
