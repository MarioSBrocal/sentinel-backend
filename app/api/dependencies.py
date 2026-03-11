from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repo import SQLAlchemyUserRepository
from app.services.user_service import UserService


def get_user_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyUserRepository:  # noqa: B008
    """Gets the user repository instance."""
    return SQLAlchemyUserRepository(db)


def get_user_service(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),  # noqa: B008
) -> UserService:
    """Gets the user service instance."""
    return UserService(user_repo=repo)
