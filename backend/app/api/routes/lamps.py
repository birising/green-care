import json
from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.db.session import get_session
from app.models import Lamp as LampModel
from app.schemas import Lamp

router = APIRouter(prefix="/lamps", tags=["lamps"])


def _to_schema(row: tuple) -> Lamp:
    point_geojson = json.loads(row.point) if row.point else None
    return Lamp(id=row.id, name=row.name, point=point_geojson)


@router.get("", response_model=list[Lamp])
async def list_lamps(session: AsyncSession = Depends(get_session)) -> Sequence[Lamp]:
    query = select(
        LampModel.id,
        LampModel.name,
        func.ST_AsGeoJSON(LampModel.point).label("point"),
    )
    result = await session.execute(query)
    rows = result.fetchall()
    return [_to_schema(row) for row in rows]
