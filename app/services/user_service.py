from app.core.errors import (
    AppError,
    DatabaseError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.result import Err, Ok, Result
from app.core.security import get_password_hash, verify_password
from app.domain.repositories import UserRepository
from app.models.user import User


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, email: str, password: str) -> Result[User, AppError]:
        """Create a new user with the given email and password."""

        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            return Err(UserAlreadyExistsError(email=email))

        hashed_pwd = get_password_hash(password)
        new_user = User(email=email, hashed_password=hashed_pwd)

        try:
            saved_user = await self.user_repo.create(new_user)
            return Ok(saved_user)
        except Exception as e:
            return Err(DatabaseError(detail=str(e)))

    async def authenticate_user(
        self, email: str, password: str
    ) -> Result[User, AppError]:
        """Verify credentials for login."""
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            return Err(InvalidCredentialsError())

        return Ok(user)

    async def get_user_by_email(self, email: str) -> Result[User, AppError]:
        """Retrieve a user by their email."""
        user = await self.user_repo.get_by_email(email)

        if user:
            return Ok(user)
        else:
            return Err(UserNotFoundError(email=email))
