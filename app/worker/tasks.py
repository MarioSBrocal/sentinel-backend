import logging
import time
import uuid
from datetime import UTC, datetime

import httpx
from redis.asyncio import Redis
from taskiq import TaskiqDepends

from app.api.dependencies import (
    get_incident_repository,
    get_monitor_repository,
    get_ping_log_repository,
    get_redis,
)
from app.models.alert_channel import AlertChannelType
from app.models.incident import Incident
from app.models.ping_log import PingLog
from app.worker.broker import broker
from app.worker.pinger import HttpPinger

logger = logging.getLogger(__name__)


@broker.task
async def ping_monitor_task(
    monitor_id: uuid.UUID,
    repo=TaskiqDepends(get_monitor_repository),  # noqa: B008
    ping_log_repo=TaskiqDepends(get_ping_log_repository),  # noqa: B008
    incident_repo=TaskiqDepends(get_incident_repository),  # noqa: B008
    redis: Redis = TaskiqDepends(get_redis),  # noqa: B008
):
    """Task to ping a monitor, log the result, and manage incidents."""
    monitor = await repo.get_by_id(monitor_id)

    if not monitor:
        logger.warning(f"Monitor {monitor_id} not found. Cancelling task.")
        return "Not Found"

    if monitor.is_paused:
        logger.info(f"Monitor {monitor.name} is paused. Skipping ping.")
        return "Paused"

    logger.info(f"Starting ping for: {monitor.name} ({monitor.url})")

    pinger = HttpPinger()
    result = await pinger.execute(
        url=str(monitor.url),
        method=monitor.method,
        headers=monitor.headers,
        body=monitor.body,
        assertions=monitor.assertions,
    )

    ping_log = PingLog(
        monitor_id=monitor.id,
        timestamp=datetime.now(UTC),
        status_code=result.status_code,
        response_time_ms=result.response_time_ms,
        is_up=result.is_up,
    )
    await ping_log_repo.create(ping_log)

    redis_failures_key = f"monitor:{monitor.id}:failures"

    if result.is_up:
        logger.info(f"UP: {monitor.name} | {result.response_time_ms}ms")

        await redis.delete(redis_failures_key)

        active_incident = await incident_repo.get_active_by_monitor(monitor.id)
        if active_incident:
            logger.info(f"🔄 RECOVERY: {monitor.name} is back online.")
            await incident_repo.resolve(active_incident.id)
            await send_incident_notification_task.kiq(
                incident_id=active_incident.id, is_recovery=True
            )

    else:
        logger.error(
            f"DOWN: {monitor.name} | {result.error_type} - {result.error_details}"
        )

        failures_count = await redis.incr(redis_failures_key)

        if failures_count == 1:
            await redis.expire(redis_failures_key, 3600)

        logger.info(f"Failure {failures_count}/3 for {monitor.name}")

        if failures_count == 3:
            active_incident = await incident_repo.get_active_by_monitor(monitor.id)

            if not active_incident:
                logger.critical(f"INCIDENT CREATED: {monitor.name} is confirmed DOWN.")

                # Crear la incidencia en Base de Datos
                new_incident = Incident(
                    monitor_id=monitor.id,
                    error_type=result.error_type,
                    error_details=result.error_details,
                )
                created_incident = await incident_repo.create(new_incident)

                await send_incident_notification_task.kiq(
                    incident_id=created_incident.id, is_recovery=False
                )

    return result.model_dump()


@broker.task
async def send_incident_notification_task(
    incident_id: int,
    is_recovery: bool,
    incident_repo=TaskiqDepends(get_incident_repository),  # noqa: B008
    monitor_repo=TaskiqDepends(get_monitor_repository),  # noqa: B008
):
    """Task to send notifications for an incident (either new or recovery) to all associated AlertChannels."""

    incident = await incident_repo.get_by_id(incident_id)
    if not incident:
        logger.error(
            f"Incident with ID {incident_id} not found. Cannot send notification."
        )
        return

    monitor = await monitor_repo.get_by_id_with_channels(incident.monitor_id)
    if not monitor or not monitor.alert_channels:
        logger.info(
            f"Monitor {incident.monitor_id} not found or has no alert channels. Skipping notification."
        )
        return

    if is_recovery:
        subject = f"SOLVED: Monitor {monitor.name} is back online"
        message = (
            f"Good news. The monitor {monitor.name} ({monitor.url}) is back online."
        )
        color = "#36a64f"  # Green for Slack / Discord
    else:
        subject = f"🚨 DOWN: The monitor {monitor.name} is failing"
        message = f"Critical alert. The monitor {monitor.name} has failed due to: {incident.error_type}."
        color = "#ff0000"  # Red for Slack / Discord

    logger.info(
        f"Sending notifications to {len(monitor.alert_channels)} channels for monitor {monitor.name}..."
    )

    async with httpx.AsyncClient() as client:
        for channel in monitor.alert_channels:
            try:
                if channel.type == AlertChannelType.EMAIL:
                    # TODO: Integrate actual email sending logic (e.g., using aiosmtplib or an email service API)
                    logger.info(
                        f"[SIMULATED EMAIL] To: {channel.destination} | Subject: {subject}"
                    )

                elif channel.type == AlertChannelType.SLACK:
                    payload = {
                        "text": subject,
                        "attachments": [{"color": color, "text": message}],
                    }
                    await client.post(channel.destination, json=payload)
                    logger.info("[SLACK] Sent notification")

                elif channel.type == AlertChannelType.DISCORD:
                    payload = {
                        "content": subject,
                        "embeds": [
                            {
                                "title": subject,
                                "description": message,
                                "color": int(color.lstrip("#"), 16),
                            }
                        ],
                    }
                    await client.post(channel.destination, json=payload)
                    logger.info("[DISCORD] Sent notification")

            except Exception as e:
                logger.error(
                    f"Failed to send notification to channel {channel.id} ({channel.type}): {e!s}"
                )


@broker.task(schedule=[{"interval": 15}])
async def dispatch_due_monitors_task(
    repo=TaskiqDepends(get_monitor_repository),  # noqa: B008
    redis: Redis = TaskiqDepends(get_redis),  # noqa: B008
):
    """Task that runs every 15 seconds to check for monitors that are due for pinging and dispatches ping tasks for them."""
    logger.info("Dispatcher: Checking for monitors due for pinging...")

    active_monitors = await repo.get_all_active()
    current_time = time.time()
    dispatched_count = 0

    for monitor in active_monitors:
        last_ping_key = f"monitor:{monitor.id}:last_ping_time"
        last_ping_time = await redis.get(last_ping_key)

        if (
            not last_ping_time
            or (current_time - float(last_ping_time)) >= monitor.interval_seconds
        ):
            await ping_monitor_task.kiq(monitor.id)

            await redis.set(last_ping_key, current_time)
            dispatched_count += 1

    if dispatched_count > 0:
        logger.info(f"Dispatcher: {dispatched_count} monitors sent to the Ping queue.")


# 'cron': '0 */6 * * *' -> Meaning: At minute 0, every 6 hours.
@broker.task(schedule=[{"cron": "0 */6 * * *"}])
async def maintain_database_partitions_task(
    repo=TaskiqDepends(get_ping_log_repository),  # noqa: B008
):
    """Task that runs every 6 hours to ensure that database partitions for Ping Logs are created and maintained."""

    logger.info("Running database partition maintenance task for Ping Logs...")
    await repo.ensure_daily_partitions()
