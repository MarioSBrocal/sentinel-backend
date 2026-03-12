import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class DailyStatBase(BaseModel):
    monitor_id: uuid.UUID
    date: date
    total_checks: int
    successful_checks: int
    avg_response_time_ms: int


class DailyStatCreate(DailyStatBase):
    """Schema for creating new daily stat entries."""

    pass


class DailyStatResponse(DailyStatBase):
    """Schema for returning daily stat data to the frontend."""

    model_config = ConfigDict(from_attributes=True)
