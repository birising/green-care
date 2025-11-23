# Backend schema and data import

## SQL schema
The raw SQL schema lives in [`schema.sql`](schema.sql) and can be applied with `psql`:

```bash
psql "$DATABASE_URL" -f backend/schema.sql
```

## Alembic migration
1. Install dependencies (example):
   ```bash
   pip install alembic geoalchemy2 psycopg2-binary sqlalchemy
   ```
2. Run the migration (from the repository root):
   ```bash
   alembic -c backend/alembic.ini -x db_url=$DATABASE_URL upgrade head
   ```

## GeoJSON import
Use the helper to import lamps or bins from a GeoJSON file (SRID 4326 expected):

```bash
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db \
python backend/scripts/import_geojson.py --kind lamps path/to/lamps.geojson

DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db \
python backend/scripts/import_geojson.py --kind bins path/to/bins.geojson
```

The script looks for properties `name`, and for bins optionally `fill_level`, `battery_level`, and `temperature` to pre-fill the latest telemetry snapshot.
