from typing import Any

from pydantic import BaseModel


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any
