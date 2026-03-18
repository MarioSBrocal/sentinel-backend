import logging
import time
import uuid
from datetime import UTC, date, datetime, timedelta

import httpx
from redis.asyncio import Redis
from taskiq import TaskiqDepends

from app.api.dependencies import (
    get_daily_stat_repository,
    get_hourly_stat_repository,
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
    monitor_result = await repo.get_by_id(monitor_id)

    if monitor_result.is_err():
        logger.warning(f"Monitor {monitor_id} not found. Cancelling task.")
        return "Not Found"

    monitor = monitor_result.unwrap()

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

        active_incident_result = await incident_repo.get_active_by_monitor(monitor.id)

        if active_incident_result.is_err():
            logger.error(
                f"Error checking active incident for monitor {monitor.name}: {active_incident_result.unwrap_err()!s}"
            )
            return result.model_dump()

        active_incident = active_incident_result.unwrap()

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
                created_incident_result = await incident_repo.create(new_incident)

                if created_incident_result.is_err():
                    logger.error(
                        f"Failed to create incident for monitor {monitor.name}: {created_incident_result.unwrap_err()!s}"
                    )
                    return result.model_dump()

                created_incident = created_incident_result.unwrap()

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

    incident_result = await incident_repo.get_by_id(incident_id)

    if incident_result.is_err():
        logger.error(
            f"Incident with ID {incident_id} not found. Cannot send notification."
        )
        return

    incident = incident_result.unwrap()

    monitor_result = await monitor_repo.get_by_id(
        incident.monitor_id, load_channels=True
    )

    if monitor_result.is_err():
        logger.error(
            f"Monitor with ID {incident.monitor_id} not found. Cannot send notification for incident {incident_id}."
        )
        return

    monitor = monitor_result.unwrap()

    if not monitor.alert_channels:
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

    active_monitors_result = await repo.get_all_active()

    if active_monitors_result.is_err():
        logger.error(
            f"Failed to retrieve active monitors: {active_monitors_result.unwrap_err()!s}"
        )
        return

    active_monitors = active_monitors_result.unwrap()

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


# 'cron': '2 * * * *' -> Meaning: At minute 2 of every hour.
@broker.task(schedule=[{"cron": "2 * * * *"}])
async def aggregate_hourly_stats(
    repo=TaskiqDepends(get_hourly_stat_repository),  # noqa: B008
) -> None:
    """Aggregate ping logs into hourly stats up to the previous closed hour."""
    now = datetime.now(UTC)
    current_hour_boundary = now.replace(minute=0, second=0, microsecond=0)

    last_processed_result = await repo.max_hour_timestamp()
    if last_processed_result.is_err():
        logger.error(
            "Failed to get max hourly stat timestamp: %s",
            last_processed_result.unwrap_err(),
        )
        return

    last_processed_hour = last_processed_result.unwrap()

    if last_processed_hour >= current_hour_boundary:
        return

    aggregate_result = await repo.aggregate_between(
        start_inclusive=last_processed_hour,
        end_exclusive=current_hour_boundary,
    )
    if aggregate_result.is_err():
        logger.error(
            "Failed to aggregate hourly stats: %s",
            aggregate_result.unwrap_err(),
        )
        return

    upserted_count = aggregate_result.unwrap()
    if upserted_count > 0:
        logger.info(
            "Hourly stats aggregated and upserted: %s rows up to %s",
            upserted_count,
            current_hour_boundary,
        )


# 'cron': '10 0 * * *' -> Meaning: At 00:10 (10 minutes after midnight) every day.
@broker.task(schedule=[{"cron": "10 0 * * *"}])  # 00:10 UTC cada día
async def aggregate_daily_stats(
    daily_repo=TaskiqDepends(get_daily_stat_repository),  # noqa: B008
    ping_log_repo=TaskiqDepends(get_ping_log_repository),  # noqa: B008
) -> None:
    """Aggregate ping logs into daily stats for each day up to yesterday (never touching the current day in course)."""
    today = datetime.now(UTC).date()
    end_day_exclusive = today

    max_date_result = await daily_repo.max_date()
    if max_date_result.is_err():
        logger.error(
            "Failed to get max daily stat date: %s", max_date_result.unwrap_err()
        )
        return

    last_processed_day = max_date_result.unwrap()

    if last_processed_day == date.min:
        start_day = await ping_log_repo.min_date()
        if start_day.is_err():
            logger.error("Failed to get min ping log date: %s", start_day.unwrap_err())
            return
        start_day = start_day.unwrap()
    else:
        start_day = last_processed_day + timedelta(days=1)

    if start_day >= end_day_exclusive:
        return

    aggregate_result = await daily_repo.aggregate_between(
        start_date=start_day,
        end_date=end_day_exclusive,
    )
    if aggregate_result.is_err():
        logger.error(
            "Failed to aggregate daily stats from %s to %s: %s",
            start_day,
            end_day_exclusive,
            aggregate_result.unwrap_err(),
        )
        return

    rows = aggregate_result.unwrap()
    if rows > 0:
        logger.info(
            "Daily stats upserted from %s to %s: %s rows",
            start_day,
            end_day_exclusive,
            rows,
        )

    current_day = start_day
    while current_day < end_day_exclusive:
        drop_day = current_day - timedelta(days=7)
        drop_result = await ping_log_repo.drop_partition_for_date(drop_day)
        if drop_result.is_err():
            logger.error(
                "Failed to drop ping_logs partition for %s: %s",
                drop_day,
                drop_result.unwrap_err(),
            )
        current_day += timedelta(days=1)
