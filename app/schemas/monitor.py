import enum
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class HTTPMethod(enum.StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


class AssertionSource(enum.StrEnum):
    STATUS_CODE = "status_code"
    RESPONSE_TIME = "response_time"
    BODY = "body"
    HEADER = "header"


class AssertionOperator(enum.StrEnum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    LESS_THAN = "less_than"
    MORE_THAN = "more_than"
    LESS_OR_EQUALS = "less_or_equals"
    MORE_OR_EQUALS = "more_or_equals"


class Assertion(BaseModel):
    source: AssertionSource
    property: str | None = (
        None  # Example: If source is HEADER, property would be "Content-Type"
    )
    operator: AssertionOperator
    target: Any  # It can be int (200) or str ("OK") depending on the source


class MonitorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl
    method: HTTPMethod = HTTPMethod.GET
    interval_seconds: int = Field(default=60, ge=15, multiple_of=15)
    headers: dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs of HTTP headers to include in the request",
    )
    assertions: list[Assertion] = Field(
        default_factory=list, description="Rules to validate the monitor is UP"
    )
    body: str | None = Field(
        default=None, description="Body of the request (text or JSON string)"
    )


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
