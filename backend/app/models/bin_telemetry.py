from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BinTelemetry(Base):
    __tablename__ = "bin_telemetry"

    id: Mapped[int] = mapped_column(primary_key=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id", ondelete="CASCADE"), nullable=False)
    fill_level: Mapped[float | None] = mapped_column(Numeric(5, 2))
    battery_level: Mapped[float | None] = mapped_column(Numeric(5, 2))
    temperature: Mapped[float | None] = mapped_column(Numeric(5, 2))
    at_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
