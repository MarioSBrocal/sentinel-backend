import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.monitor import Monitor


class IncidentType(enum.StrEnum):
    DNS_ERROR = "dns_error"  # Couldn't resolve the domain name
    CONNECTION_REFUSED = (
        "connection_refused"  # The server refuses the connection (e.g., closed port)
    )
    SSL_ERROR = "ssl_error"  # Expired or invalid certificate
    TIMEOUT = "timeout"  # Took too long (to connect or respond)
    HTTP_ERROR = "http_error"  # Responded, but with an error (4xx, 5xx)
    ASSERTION_FAILED = (
        "assertion_failed"  # Responded 200 OK, but failed the user's rule
    )
    UNKNOWN_ERROR = "unknown_error"  # Catch-all for unexpected issues


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    monitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monitors.id", ondelete="CASCADE")
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    error_type: Mapped[IncidentType] = mapped_column(
        Enum(IncidentType, native_enum=False, length=50), nullable=False
    )
    error_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    monitor: Mapped[Monitor] = relationship()
