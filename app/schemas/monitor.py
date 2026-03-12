import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class HTTPMethod(enum.StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


class MonitorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl
    method: HTTPMethod = HTTPMethod.GET
    interval_seconds: int = Field(default=60, ge=15, multiple_of=15)


class MonitorCreate(MonitorBase):
    """Datos necesarios para crear un monitor."""

    pass


class MonitorResponse(MonitorBase):
    """Datos que devolvemos al frontend."""

    id: uuid.UUID
    user_id: uuid.UUID
    is_paused: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
