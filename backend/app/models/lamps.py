from geoalchemy2 import Geometry
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Lamp(Base):
    __tablename__ = "lamps"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    point: Mapped[object] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
