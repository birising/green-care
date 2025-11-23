# System architecture

The system consists of a FastAPI backend (PostgreSQL + PostGIS), a React + Leaflet frontend, and a Traefik reverse-proxy that terminates HTTPS. All components are orchestrated via Docker Compose for local development.

## Components
- **Frontend**: React (TypeScript, Vite) with Leaflet rendering polygons (greens) and points (lamps, bins). Data is fetched via React Query from `/api/v1`.
- **Backend**: FastAPI with async SQLAlchemy/asyncpg. Exposes CRUD-ish list/detail endpoints for greens, lamps, bins, plus protected telemetry ingestion and listing for bins.
- **Database**: PostgreSQL with PostGIS extension for spatial storage and indexes.
- **Reverse proxy**: Traefik handles TLS termination on :443 and routes `/api` to backend, everything else to frontend.

## Communication
- Browser → Traefik over HTTPS (self-signed cert for dev).
- Traefik → Frontend container (`/`) and backend container (`/api`) over the internal Docker network using HTTP.
- Backend connects to PostGIS over the backend network using the `DATABASE_URL` provided by environment variables.

## Data model
Tables (SRID 4326):
- **greens**: id, name, polygon (geometry), frequency_days, last_mowed_at
- **lamps**: id, name, point (geometry)
- **bins**: id, name, point (geometry), last_fill_level, last_battery_level, last_temperature, updated_at
- **bin_telemetry**: id, bin_id, fill_level, battery_level, temperature, at_time
- **lamp_issues / bin_issues**: id, FK, status (open, in_progress, resolved), type, description, reported_by, reported_at, resolved_at, resolution_note

## Telemetry & authentication
- The endpoint `POST /api/v1/bins/{bin_id}/telemetry` requires an `X-API-TOKEN` header.
- Allowed tokens are configured via environment variable `API_TOKENS` (CSV string).
- Requests without a valid token return HTTP 401.
- Telemetry records are persisted to `bin_telemetry` with timestamps; listing is available at `GET /api/v1/bins/{bin_id}/telemetry`.

## Issue workflow
1. Client fetches assets (greens/lamps/bins) and displays them on the map.
2. Users can report lamp or bin issues (planned endpoints) with status transitions (`open` → `in_progress` → `resolved`).
3. Admin PATCH endpoints (planned) update issue status/resolution notes; history is stored per issue record.

## Deployment
- Local dev via Docker Compose using the provided `docker-compose.yml` and self-signed cert in `infra/certs`.
- Traefik listens on 443; frontend/backend are on the shared `web` network; PostGIS is isolated on `backend` network.
