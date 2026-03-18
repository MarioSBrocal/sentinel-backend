from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.api.dependencies import get_user_service
from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
)
from app.schemas.token import Token, TokenRefreshRequest
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
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(request: TokenRefreshRequest):
    """Takes a refresh token and returns a new access token if the refresh token is valid."""
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: refresh token expected",
            )

        if user_email is None:
            raise HTTPException(
                status_code=401, detail="Invalid token: subject missing"
            )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from e

    new_access_token = create_access_token(data={"sub": user_email})

    return Token(access_token=new_access_token, refresh_token=request.refresh_token)
