from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import GeoJSONGeometry


class Green(BaseModel):
    id: int
    name: str
    polygon: GeoJSONGeometry
    frequency_days: int
    last_mowed_at: datetime | None = None
