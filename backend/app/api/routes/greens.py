import json
from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.db.session import get_session
from app.models import Green as GreenModel
from app.schemas import Green

router = APIRouter(prefix="/greens", tags=["greens"])


def _to_schema(row: tuple) -> Green:
    polygon_geojson = json.loads(row.polygon) if row.polygon else None
    return Green(
        id=row.id,
        name=row.name,
        polygon=polygon_geojson,
        frequency_days=row.frequency_days,
        last_mowed_at=row.last_mowed_at,
    )


@router.get("", response_model=list[Green])
async def list_greens(session: AsyncSession = Depends(get_session)) -> Sequence[Green]:
    query = select(
        GreenModel.id,
        GreenModel.name,
        func.ST_AsGeoJSON(GreenModel.polygon).label("polygon"),
        GreenModel.frequency_days,
        GreenModel.last_mowed_at,
    )
    result = await session.execute(query)
    rows = result.fetchall()
    return [_to_schema(row) for row in rows]
