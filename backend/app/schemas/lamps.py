from pydantic import BaseModel

from app.schemas.common import GeoJSONGeometry


class Lamp(BaseModel):
    id: int
    name: str
    point: GeoJSONGeometry
