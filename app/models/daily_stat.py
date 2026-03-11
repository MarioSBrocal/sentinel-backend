import datetime
import uuid

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DailyStat(Base):
    __tablename__ = "daily_stats"

    monitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("monitors.id", ondelete="CASCADE"), primary_key=True
    )
    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)

    total_checks: Mapped[int] = mapped_column(Integer, nullable=False)
    successful_checks: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
