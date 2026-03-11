from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Create the asynchronous engine
engine = create_async_engine(
    str(settings.database_url),
    echo=settings.environment == "development",
    future=True,
    pool_pre_ping=True,
)

# Create the session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    Dependency function to provide a database session for each request.
    It yields the session to the route and ensures it gets safely closed afterwards.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
