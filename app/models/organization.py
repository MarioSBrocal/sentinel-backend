import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert_channel import AlertChannel
    from app.models.monitor import Monitor
    from app.models.organization_user import OrganizationUser


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    members: Mapped[list[OrganizationUser]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    monitors: Mapped[list[Monitor]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    alert_channels: Mapped[list[AlertChannel]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
