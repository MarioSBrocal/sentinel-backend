from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.core.errors import TokenError
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(
    tags=["users"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": TokenError().message}},
)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    """Endpoint to get the current authenticated user's information."""
    return current_user
