import uuid
from datetime import UTC, datetime
from typing import override

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiKeyNotFoundError, AppError, DatabaseError
from app.core.result import Err, Ok, Result
from app.domain.repositories import ApiKeyRepository
from app.models.api_key import ApiKey


class SQLAlchemyApiKeyRepository(ApiKeyRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    @override
    async def create(self, api_key: ApiKey) -> Result[ApiKey, AppError]:
        self.db.add(api_key)

        try:
            await self.db.commit()
            await self.db.refresh(api_key)
            return Ok(api_key)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(str(e)))

    @override
    async def get_by_user_id(
        self, user_id: uuid.UUID
    ) -> Result[list[ApiKey], AppError]:
        result = await self.db.execute(select(ApiKey).where(ApiKey.user_id == user_id))
        return Ok(list(result.scalars().all()))

    @override
    async def get_by_hashed_key(self, hashed_key: str) -> Result[ApiKey, AppError]:
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.hashed_key == hashed_key)
        )
        api_key = result.scalars().first()
        if api_key is None:
            return Err(ApiKeyNotFoundError())
        return Ok(api_key)

    @override
    async def update_last_used(self, api_key_id: uuid.UUID) -> Result[None, AppError]:
        result = await self.db.execute(select(ApiKey).where(ApiKey.id == api_key_id))
        api_key = result.scalars().first()
        if api_key is None:
            return Err(ApiKeyNotFoundError())

        api_key.last_used_at = datetime.now(UTC)

        try:
            await self.db.commit()
            return Ok(None)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(str(e)))

    @override
    async def delete(self, api_key: ApiKey) -> Result[None, AppError]:
        await self.db.delete(api_key)

        try:
            await self.db.commit()
            return Ok(None)
        except IntegrityError as e:
            await self.db.rollback()
            return Err(DatabaseError(str(e)))
