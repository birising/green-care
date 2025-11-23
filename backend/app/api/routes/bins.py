import json
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.db.session import get_session
from app.models import Bin as BinModel
from app.schemas import Bin

router = APIRouter(prefix="/bins", tags=["bins"])


def _to_schema(row: tuple) -> Bin:
    point_geojson = json.loads(row.point) if row.point else None
    return Bin(
        id=row.id,
        name=row.name,
        point=point_geojson,
        last_fill_level=float(row.last_fill_level) if row.last_fill_level is not None else None,
        last_battery_level=float(row.last_battery_level) if row.last_battery_level is not None else None,
        last_temperature=float(row.last_temperature) if row.last_temperature is not None else None,
        updated_at=row.updated_at,
    )


@router.get("", response_model=list[Bin])
async def list_bins(session: AsyncSession = Depends(get_session)) -> Sequence[Bin]:
    query = select(
        BinModel.id,
        BinModel.name,
        func.ST_AsGeoJSON(BinModel.point).label("point"),
        BinModel.last_fill_level,
        BinModel.last_battery_level,
        BinModel.last_temperature,
        BinModel.updated_at,
    )
    result = await session.execute(query)
    rows = result.fetchall()
    return [_to_schema(row) for row in rows]


@router.get("/{bin_id}", response_model=Bin)
async def get_bin(bin_id: int, session: AsyncSession = Depends(get_session)) -> Bin:
    query = select(
        BinModel.id,
        BinModel.name,
        func.ST_AsGeoJSON(BinModel.point).label("point"),
        BinModel.last_fill_level,
        BinModel.last_battery_level,
        BinModel.last_temperature,
        BinModel.updated_at,
    ).where(BinModel.id == bin_id)

    result = await session.execute(query)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Bin not found")

    return _to_schema(row)
