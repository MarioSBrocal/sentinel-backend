from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_user_service
from app.core.security import create_access_token
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),  # noqa: B008
):
    result = await user_service.create_user(
        email=user_in.email, password=user_in.password
    )

    if result.is_err():
        raise result.unwrap_err()

    return result.unwrap()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    user_service: UserService = Depends(get_user_service),  # noqa: B008
):
    result = await user_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )

    if result.is_err():
        raise result.unwrap_err()

    user = result.unwrap()
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")
