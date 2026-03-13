from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

import app.worker.tasks  # noqa: F401
from app.worker.broker import broker

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
