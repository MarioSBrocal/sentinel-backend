import uuid

from app.core.errors import AppError
from app.core.result import Err, Ok, Result
from app.core.security import generate_api_key
from app.domain.repositories import ApiKeyRepository
from app.models.api_key import ApiKey


class ApiKeyService:
    def __init__(self, api_key_repo: ApiKeyRepository):
        self.api_key_repo = api_key_repo

    async def create_api_key(
        self, name: str, user_id: uuid.UUID
    ) -> Result[tuple[str, ApiKey], AppError]:
        raw_key, prefix, hashed_key = generate_api_key()
        api_key = ApiKey(
            name=name, prefix=prefix, hashed_key=hashed_key, user_id=user_id
        )

        result = await self.api_key_repo.create(api_key)

        if result.is_err():
            return Err(result.unwrap_err())

        return Ok((raw_key, result.unwrap()))

    async def get_api_keys_for_user(
        self, user_id: uuid.UUID
    ) -> Result[list[ApiKey], AppError]:
        return await self.api_key_repo.get_by_user_id(user_id)

    async def get_api_key_by_hash(self, hashed_key: str) -> Result[ApiKey, AppError]:
        return await self.api_key_repo.get_by_hashed_key(hashed_key)

    async def update_last_used(self, api_key_id: uuid.UUID) -> Result[None, AppError]:
        return await self.api_key_repo.update_last_used(api_key_id)

    async def delete_api_key_by_hash(self, hashed_key: str) -> Result[None, AppError]:
        get_result = await self.api_key_repo.get_by_hashed_key(hashed_key)

        if get_result.is_err():
            return Err(get_result.unwrap_err())

        api_key = get_result.unwrap()
        return await self.api_key_repo.delete(api_key)
