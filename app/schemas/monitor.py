import enum
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.monitor import HTTPMethod


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


def default_assertions() -> list[Assertion]:
    """Default assertion to ensure the monitor is UP if the user doesn't provide any."""
    return [
        Assertion(
            source=AssertionSource.STATUS_CODE,
            operator=AssertionOperator.EQUALS,
            target=200,
        )
    ]


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
        default_factory=default_assertions,
        description="Rules to validate the monitor is UP",
    )
    body: dict[str, Any] | None = Field(
        default=None, description="Body of the request (text or JSON string)"
    )


class MonitorCreate(MonitorBase):
    """Schema for registering new monitors."""

    organization_id: uuid.UUID | None = Field(
        default=None, description="ID of the organization to which the monitor belongs"
    )


class MonitorResponse(MonitorBase):
    """Schema for returning monitor data to the frontend."""

    id: uuid.UUID
    user_id: uuid.UUID | None
    organization_id: uuid.UUID | None
    is_paused: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
