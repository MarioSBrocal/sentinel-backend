import uuid
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, DatabaseError, UserNotFoundError
from app.core.result import Err, Ok, Result
from app.domain.repositories import UserRepository
from app.models.user import User


class SQLAlchemyUserRepository(UserRepository):
    """A repository implementation for User entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, user: User) -> Result[User, AppError]:
        self.db.add(user)

        try:
            await self.db.commit()
            await self.db.refresh(user)
            return Ok(user)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(detail=str(e)))

    @override
    async def get_by_id(self, user_id: uuid.UUID) -> Result[User, AppError]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return Err(UserNotFoundError(user_id=user_id))
        return Ok(user)

    @override
    async def get_by_email(self, email: str) -> Result[User, AppError]:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            return Err(UserNotFoundError(email=email))
        return Ok(user)
