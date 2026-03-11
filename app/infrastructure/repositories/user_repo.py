from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import UserRepository
from app.models.user import User


class SQLAlchemyUserRepository(UserRepository):
    """A repository implementation for User entities using SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @override
    async def create(self, user: User) -> User:
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise
