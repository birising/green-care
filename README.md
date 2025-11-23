# Green Care Interactive Map

An interactive map for visualizing municipal green areas, street lamps, and waste bins with live telemetry. The project ships a React + TypeScript frontend, FastAPI backend with PostGIS, and Docker-based infrastructure with HTTPS termination.

## Tech stack
- Frontend: React, TypeScript, Vite, React Query, Leaflet
- Backend: FastAPI, SQLAlchemy (async + asyncpg), Alembic, PostgreSQL + PostGIS
- Infra: Docker Compose, Traefik reverse-proxy with self-signed TLS for local dev

## Repository layout
```
backend/          # FastAPI application, models, schemas, migrations, tests
frontend/         # React + Vite application with Leaflet map
infra/            # Traefik config and dev TLS certs
infra/certs       # Self-signed localhost cert used by Traefik
docs/             # Architecture and API docs
ARCHITECTURE.md   # High-level architecture blueprint
docker-compose.yml
```

## Running the backend locally
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs on `http://localhost:8000`, Swagger at `http://localhost:8000/docs`.

## Running the frontend locally
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173` and expects the API at `/api/v1` (configure via `VITE_API_BASE_URL`).

## Running everything with Docker + HTTPS
```bash
docker-compose build
docker-compose up
```
Services exposed via Traefik on `https://localhost`:
- Frontend: `https://localhost`
- API: `https://localhost/api/v1`
- Swagger: `https://localhost/api/docs` (proxied)

The compose file provisions PostGIS, builds frontend/backend images, and mounts a self-signed TLS certificate from `infra/certs`.
Browsers will show a warning for the self-signed certificate—accept it locally or import the CA as trusted for development.
