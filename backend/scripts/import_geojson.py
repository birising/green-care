"""Import lamps and bins from a GeoJSON file into PostgreSQL/PostGIS.

Usage:
    DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db \
    python backend/scripts/import_geojson.py --kind lamps data/lamps.geojson

    DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db \
    python backend/scripts/import_geojson.py --kind bins data/bins.geojson
"""
import argparse
import json
import os
from pathlib import Path

from sqlalchemy import Column, BigInteger, DateTime, MetaData, Numeric, Table, Text, create_engine, text
from geoalchemy2 import Geometry

metadata = MetaData()

lamps = Table(
    "lamps",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", Text, nullable=False),
    Column("point", Geometry("POINT", srid=4326), nullable=False),
)

bins = Table(
    "bins",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", Text, nullable=False),
    Column("point", Geometry("POINT", srid=4326), nullable=False),
    Column("last_fill_level", Numeric(5, 2)),
    Column("last_battery_level", Numeric(5, 2)),
    Column("last_temperature", Numeric(5, 2)),
    Column("updated_at", DateTime(timezone=True)),
)


def load_features(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features", [])
    return features


def insert_lamps(engine, features: list[dict]):
    stmt = text(
        """
        INSERT INTO lamps (name, point)
        VALUES (:name, ST_SetSRID(ST_GeomFromGeoJSON(:geom)::geometry, 4326))
        """
    )
    with engine.begin() as conn:
        for feature in features:
            name = feature.get("properties", {}).get("name") or "Unnamed lamp"
            geom_json = json.dumps(feature.get("geometry"))
            conn.execute(stmt, {"name": name, "geom": geom_json})


def insert_bins(engine, features: list[dict]):
    stmt = text(
        """
        INSERT INTO bins (
            name, point, last_fill_level, last_battery_level, last_temperature
        )
        VALUES (
            :name,
            ST_SetSRID(ST_GeomFromGeoJSON(:geom)::geometry, 4326),
            :last_fill_level,
            :last_battery_level,
            :last_temperature
        )
        """
    )
    with engine.begin() as conn:
        for feature in features:
            props = feature.get("properties", {})
            name = props.get("name") or "Unnamed bin"
            geom_json = json.dumps(feature.get("geometry"))
            conn.execute(
                stmt,
                {
                    "name": name,
                    "geom": geom_json,
                    "last_fill_level": props.get("fill_level"),
                    "last_battery_level": props.get("battery_level"),
                    "last_temperature": props.get("temperature"),
                },
            )


def main():
    parser = argparse.ArgumentParser(description="Import lamps or bins from GeoJSON")
    parser.add_argument("geojson", type=Path, help="Path to GeoJSON file")
    parser.add_argument("--kind", choices=["lamps", "bins"], required=True, help="Which entity to import")
    parser.add_argument(
        "--database-url",
        dest="database_url",
        default=None,
        help="SQLAlchemy connection string (default: env DATABASE_URL)",
    )

    args = parser.parse_args()

    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL must be provided via --database-url or environment variable")

    engine = create_engine(database_url, future=True)

    features = load_features(args.geojson)
    if args.kind == "lamps":
        insert_lamps(engine, features)
    else:
        insert_bins(engine, features)

    print(f"Imported {len(features)} features into {args.kind}.")


if __name__ == "__main__":
    main()
