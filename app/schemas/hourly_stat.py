import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HourlyStatBase(BaseModel):
    monitor_id: uuid.UUID
    hour_timestamp: datetime
    total_checks: int
    successful_checks: int
    avg_response_time_ms: int


class HourlyStatCreate(HourlyStatBase):
    """Schema for creating new hourly stat entries."""

    pass


class HourlyStatResponse(HourlyStatBase):
    """Schema for returning hourly stat data to the frontend."""

    model_config = ConfigDict(from_attributes=True)
