import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HourlyStat(Base):
    __tablename__ = "hourly_stats"

    monitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monitors.id", ondelete="CASCADE"), primary_key=True
    )
    hour_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True
    )

    total_checks: Mapped[int] = mapped_column(Integer, nullable=False)
    successful_checks: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
