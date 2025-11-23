from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Green(Base):
    __tablename__ = "greens"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    polygon: Mapped[object] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    frequency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_mowed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
