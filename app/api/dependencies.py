from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import TokenError
from app.core.security import ALGORITHM
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.alert_channel_repo import (
    SQLAlchemyAlertChannelRepository,
)
from app.infrastructure.repositories.daily_stat_repo import (
    SQLAlchemyDailyStatRepository,
)
from app.infrastructure.repositories.hourly_stat_repo import (
    SQLAlchemyHourlyStatRepository,
)
from app.infrastructure.repositories.incident_repo import SQLAlchemyIncidentRepository
from app.infrastructure.repositories.monitor_repo import SQLAlchemyMonitorRepository
from app.infrastructure.repositories.ping_log_repo import SQLAlchemyPingLogRepository
from app.infrastructure.repositories.user_repo import SQLAlchemyUserRepository
from app.models.user import User
from app.schemas.token import TokenData
from app.services.alert_channel_service import AlertChannelService
from app.services.daily_stat_service import DailyStatService
from app.services.hourly_stat_service import HourlyStatService
from app.services.incident_service import IncidentService
from app.services.monitor_service import MonitorService
from app.services.ping_log_service import PingLogService
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


def get_alert_channel_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> SQLAlchemyAlertChannelRepository:
    return SQLAlchemyAlertChannelRepository(db)


def get_alert_channel_service(
    repo: SQLAlchemyAlertChannelRepository = Depends(get_alert_channel_repository),  # noqa: B008
) -> AlertChannelService:
    return AlertChannelService(channel_repo=repo)


def get_incident_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> SQLAlchemyIncidentRepository:
    return SQLAlchemyIncidentRepository(db)


def get_incident_service(
    repo: SQLAlchemyIncidentRepository = Depends(get_incident_repository),  # noqa: B008
) -> IncidentService:
    return IncidentService(incident_repo=repo)


def get_daily_stat_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> SQLAlchemyDailyStatRepository:
    return SQLAlchemyDailyStatRepository(db)


def get_daily_stat_service(
    repo: SQLAlchemyDailyStatRepository = Depends(get_daily_stat_repository),  # noqa: B008
) -> DailyStatService:
    return DailyStatService(daily_stat_repo=repo)


def get_hourly_stat_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> SQLAlchemyHourlyStatRepository:
    return SQLAlchemyHourlyStatRepository(db)


def get_hourly_stat_service(
    repo: SQLAlchemyHourlyStatRepository = Depends(get_hourly_stat_repository),  # noqa: B008
) -> HourlyStatService:
    return HourlyStatService(hourly_stat_repo=repo)


def get_ping_log_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> SQLAlchemyPingLogRepository:
    return SQLAlchemyPingLogRepository(db)


def get_ping_log_service(
    repo: SQLAlchemyPingLogRepository = Depends(get_ping_log_repository),  # noqa: B008
) -> PingLogService:
    return PingLogService(ping_log_repo=repo)
