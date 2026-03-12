import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PingLogBase(BaseModel):
    monitor_id: uuid.UUID
    timestamp: datetime
    response_time_ms: int
    status_code: int | None
    is_up: bool


class PingLogCreate(PingLogBase):
    """Schema for creating new ping log entries."""

    pass


class PingLogResponse(PingLogBase):
    """Schema for returning ping log data to the frontend."""

    id: int

    model_config = ConfigDict(from_attributes=True)
