from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import GeoJSONGeometry


class Bin(BaseModel):
    id: int
    name: str
    point: GeoJSONGeometry
    last_fill_level: float | None = None
    last_battery_level: float | None = None
    last_temperature: float | None = None
    updated_at: datetime | None = None
