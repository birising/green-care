
# Backend schema, data import, and API

## FastAPI application

### Configuration
Copy `.env.example` to `.env` and fill in your database connection string (asyncpg driver):

```bash
cp backend/.env.example backend/.env
```

### Run the API
Install dependencies and start uvicorn from the repository root:

```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Health check: `GET http://localhost:8000/health`

Available routers under the `/api/v1` prefix:
- `GET /greens`
- `GET /lamps`
- `GET /bins`
- `GET /bins/{id}`

### Run tests
The API layer can be smoke-tested without a database using the bundled fakes:

```bash
pip install -r backend/requirements.txt
pytest backend/tests
```

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
