import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    TypeAdapter,
    model_validator,
)

from app.models.alert_channel import AlertChannelType


class AlertChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: AlertChannelType = AlertChannelType.EMAIL
    destination: str = Field(
        ..., description="Email address or URL depending on the type"
    )

    @model_validator(mode="after")
    def validate_destination(self) -> AlertChannelBase:
        """Validate the destination field based on the type of alert channel."""

        if self.type == AlertChannelType.EMAIL:
            TypeAdapter(EmailStr).validate_python(self.destination)
        elif self.type in (
            AlertChannelType.SLACK,
            AlertChannelType.DISCORD,
            AlertChannelType.WEBHOOK,
        ):
            TypeAdapter(HttpUrl).validate_python(self.destination)

        return self


class AlertChannelCreate(AlertChannelBase):
    pass


class AlertChannelResponse(AlertChannelBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
