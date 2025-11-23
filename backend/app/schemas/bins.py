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



class TelemetryInput(BaseModel):
    fill_level: float | None = None
    battery_level: float | None = None
    temperature: float | None = None
    at_time: datetime | None = None


class Telemetry(BaseModel):
    id: int
    bin_id: int
    fill_level: float | None = None
    battery_level: float | None = None
    temperature: float | None = None
    at_time: datetime
