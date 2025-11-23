import json

from datetime import datetime, timezone

from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func


from app.api.deps import require_api_token
from app.db.session import get_session
from app.models import Bin as BinModel
from app.models import BinTelemetry
from app.schemas import Bin, Telemetry, TelemetryInput

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



def _telemetry_to_schema(row: tuple) -> Telemetry:
    return Telemetry(
        id=row.id,
        bin_id=row.bin_id,
        fill_level=float(row.fill_level) if row.fill_level is not None else None,
        battery_level=float(row.battery_level) if row.battery_level is not None else None,
        temperature=float(row.temperature) if row.temperature is not None else None,
        at_time=row.at_time,
    )


@router.post("/{bin_id}/telemetry", response_model=Telemetry, status_code=201, dependencies=[Depends(require_api_token)])
async def create_bin_telemetry(
    bin_id: int,
    payload: TelemetryInput,
    session: AsyncSession = Depends(get_session),
) -> Telemetry:
    telemetry = BinTelemetry(
        bin_id=bin_id,
        fill_level=payload.fill_level,
        battery_level=payload.battery_level,
        temperature=payload.temperature,
        at_time=payload.at_time or datetime.now(timezone.utc),
    )
    session.add(telemetry)
    await session.commit()
    await session.refresh(telemetry)
    return _telemetry_to_schema(telemetry)


@router.get("/{bin_id}/telemetry", response_model=list[Telemetry])
async def list_bin_telemetry(
    bin_id: int,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
) -> list[Telemetry]:
    query = (
        select(
            BinTelemetry.id,
            BinTelemetry.bin_id,
            BinTelemetry.fill_level,
            BinTelemetry.battery_level,
            BinTelemetry.temperature,
            BinTelemetry.at_time,
        )
        .where(BinTelemetry.bin_id == bin_id)
        .order_by(BinTelemetry.at_time.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    rows = result.fetchall()
    return [_telemetry_to_schema(row) for row in rows]
