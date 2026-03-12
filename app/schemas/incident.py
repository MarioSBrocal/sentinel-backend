import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.incident import IncidentType


class DNSDetails(BaseModel):
    """Template for DNS resolution errors"""

    hostname: str
    error_message: str = Field(description="Example: Name or service not known")


class SSLDetails(BaseModel):
    """Template for SSL errors"""

    reason: str = Field(description="Example: CERTIFICATE_VERIFY_FAILED")
    issuer: str | None = None
    days_to_expire: int | None = None


class TimeoutDetails(BaseModel):
    """Template for Timeout errors"""

    phase: str = Field(description="Example: 'connection', 'read', 'ssl_handshake'")
    elapsed_ms: int
    limit_ms: int


class HTTPErrorDetails(BaseModel):
    """Template for HTTP errors"""

    status_code: int
    reason_phrase: str = Field(description="Example: Not Found, Internal Server Error")
    response_snippet: str | None = Field(
        None,
        description="Example: The first 200 characters of the response body for debugging purposes",
    )
    headers: dict[str, str] = Field(default_factory=dict)


class AssertionFailedDetails(BaseModel):
    """Template for Assertion Failed errors"""

    assertion_source: str = Field(description="Example: status_code, body, header")
    expected_value: Any
    actual_value: Any
    message: str = Field(
        description="Example: Expected status code to be 200 but got 500"
    )


class UnknownErrorDetails(BaseModel):
    """Template for unexpected errors that don't fit other categories"""

    exception_type: str
    traceback_snippet: str


INCIDENT_TEMPLATES = {
    IncidentType.DNS_ERROR: DNSDetails,
    IncidentType.SSL_ERROR: SSLDetails,
    IncidentType.TIMEOUT: TimeoutDetails,
    IncidentType.HTTP_ERROR: HTTPErrorDetails,
    IncidentType.ASSERTION_FAILED: AssertionFailedDetails,
    IncidentType.UNKNOWN_ERROR: UnknownErrorDetails,
}


class IncidentBase(BaseModel):
    monitor_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=100)
    error_type: IncidentType
    error_details: dict[str, Any] | None = Field(
        default=None,
        description="JSON with specific details about the incident, structure varies based on error_type",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_error_details(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        error_type = data.get("error_type")
        error_details = data.get("error_details")
        if not error_type or not error_details:
            return data

        TemplateClass = INCIDENT_TEMPLATES.get(IncidentType(error_type))
        if not TemplateClass:
            return data

        TemplateClass.model_validate(
            error_details
        )  # This will raise a ValidationError if the structure is wrong


class IncidentCreate(IncidentBase):
    """Schema for registering new incidents."""

    pass


class IncidentResponse(IncidentBase):
    """Schema for returning incident data to the frontend."""

    started_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
