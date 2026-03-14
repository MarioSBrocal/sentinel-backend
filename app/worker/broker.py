import taskiq_fastapi
from taskiq import TaskiqEvents
from taskiq_redis import ListQueueBroker

from app.core.config import settings
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.repositories.ping_log_repo import SQLAlchemyPingLogRepository

broker = ListQueueBroker(
    url=settings.redis_url,
)


@broker.on_event(TaskiqEvents.CLIENT_STARTUP)
@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def setup_database_partitions(state):
    """On worker startup, ensure that database partitions for Ping Logs are created for today and tomorrow."""

    print("Setting up database partitions for Ping Logs...")

    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyPingLogRepository(session)
        try:
            await repo.ensure_daily_partitions()
            print("Database partitions for Ping Logs are set up.")
        except Exception as e:
            print(f"Error setting up database partitions: {e!s}")


taskiq_fastapi.init(broker, "app.main:app")
