from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Bin(Base):
    __tablename__ = "bins"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    point: Mapped[object] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    last_fill_level: Mapped[float | None] = mapped_column(Numeric(5, 2))
    last_battery_level: Mapped[float | None] = mapped_column(Numeric(5, 2))
    last_temperature: Mapped[float | None] = mapped_column(Numeric(5, 2))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
