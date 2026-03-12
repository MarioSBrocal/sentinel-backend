from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import TokenError
from app.core.security import ALGORITHM
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.monitor_repo import SQLAlchemyMonitorRepository
from app.infrastructure.repositories.user_repo import SQLAlchemyUserRepository
from app.models.user import User
from app.schemas.token import TokenData
from app.services.monitor_service import MonitorService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyUserRepository:  # noqa: B008
    """Gets the user repository instance."""
    return SQLAlchemyUserRepository(db)


def get_user_service(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),  # noqa: B008
) -> UserService:
    """Gets the user service instance."""
    return UserService(user_repo=repo)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),  # noqa: B008
) -> User:
    """Validates the JWT token and retrieves the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=TokenError().message,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
    except JWTError as e:
        raise credentials_exception from e

    if token_data.email is None:
        raise credentials_exception
    result = await user_service.get_user_by_email(email=token_data.email)

    if result.is_err():
        raise credentials_exception

    return result.unwrap()


def get_monitor_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> SQLAlchemyMonitorRepository:
    """Gets the monitor repository instance."""
    return SQLAlchemyMonitorRepository(db)


def get_monitor_service(
    repo: SQLAlchemyMonitorRepository = Depends(get_monitor_repository),  # noqa: B008
) -> MonitorService:
    """Gets the monitor service instance."""
    return MonitorService(monitor_repo=repo)
