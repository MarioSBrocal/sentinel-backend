import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from app.core.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt and returns the hashed password as a string."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT access token with the given data and expiration time."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))

    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT refresh token with the given data and expiration time."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(days=7))

    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_api_key() -> tuple[str, str, str]:
    """Generates a new API key, returning the raw key, its prefix, and the hashed version for storage."""
    raw_key = f"sent_{secrets.token_urlsafe(32)}"
    prefix = raw_key[:8]
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()

    return raw_key, prefix, hashed_key


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verifies if the raw API key matches the hash stored in the database."""
    return hashlib.sha256(plain_api_key.encode()).hexdigest() == hashed_api_key
