# Interactive Municipality Map – Architecture Blueprint

## Directory layout
```
/frontend
  ├─ src/
  │   ├─ api/            # React Query client and hooks
  │   ├─ components/     # UI components and map widgets
  │   ├─ features/
  │   │   ├─ greens/
  │   │   ├─ lamps/
  │   │   ├─ bins/
  │   │   └─ telemetry/
  │   ├─ pages/          # top-level screens
  │   ├─ routes/         # router configuration
  │   ├─ types/          # shared TS types (DTOs)
  │   └─ utils/
  ├─ public/
  ├─ vite.config.ts (or webpack)
  └─ package.json

/backend
  ├─ app/
  │   ├─ api/
  │   │   ├─ v1/
  │   │   │   ├─ routers/        # FastAPI APIRouter per entity
  │   │   │   └─ dependencies.py
  │   ├─ core/                   # config, security, logging
  │   ├─ db/
  │   │   ├─ models/             # SQLAlchemy + GIS types
  │   │   ├─ schemas/            # Pydantic DTOs
  │   │   ├─ repositories/
  │   │   └─ session.py
  │   ├─ services/               # business logic (telemetry, issues)
  │   ├─ geo/
  │   │   ├─ data/               # stored GeoJSON assets
  │   │   └─ import_scripts/     # ETL scripts importing to DB
  │   └─ main.py
  ├─ alembic/                    # migrations
  ├─ tests/
  ├─ pyproject.toml / requirements.txt
  └─ Dockerfile

/infra
  ├─ docker-compose.yml          # local development
  ├─ traefik/ or nginx/
  │   ├─ traefik.yml / nginx.conf
  │   └─ certs/                  # TLS certificates / ACME storage
  ├─ k8s/                        # helm/chart or manifests (optional)
  └─ .env.example
```

## Docker packaging
- **Frontend**: Build static bundle with Vite/webpack in a Node (alpine) builder image; serve via `nginx:alpine` as the `frontend` container.
- **Backend**: Python slim base image with `uvicorn` (behind `gunicorn` workers) and dependencies via `poetry`/`pip`; exposed as the `backend` container.
- **Database**: `postgis/postgis` image with a persistent volume, as the `db` container.
- **Reverse proxy**: `traefik` (recommended for automatic ACME) or `nginx` container for TLS termination and routing to `frontend` and `backend`.
- **Migrations**: one-off `alembic` job (sidecar/command) executed during deployment.
- **Geo import**: short-lived job/container reusing the backend image to run scripts from `app/geo/import_scripts`.

## HTTPS termination
- TLS terminates at the reverse proxy (Traefik/Nginx) on port 443.
- Backend and frontend run over HTTP behind the proxy on the internal network/bridge.
- With Traefik, enable the `acme` resolver for Let’s Encrypt; with Nginx, store certificates in `/infra/traefik/certs` or a K8s secret.

## Frontend ↔ backend communication
- Frontend uses React Query with a base `apiClient` (`fetch`/`axios`) pointing to `/api`.
- The reverse proxy routes `/api` to the backend (e.g., `backend:8000`) and `/` to the frontend static bundle.
- CORS restricted to the frontend origin; authentication (if needed) via JWT or a `SameSite=strict` session cookie.

## GeoJSON and import scripts
- GeoJSON source files live in `/backend/app/geo/data/`.
- Import/ETL scripts live in `/backend/app/geo/import_scripts/` (e.g., `load_greens.py`, `load_lamps.py`).
- Scripts load GeoJSON, ensure EPSG:4326, and write into PostGIS tables defined below.

## Data model (SQLAlchemy + PostGIS)
- `greens`: area features (Polygon/MultiPolygon) with `id`, `name`, `type`, `area_m2`, `geom`.
- `lamps`: point features (`geometry(Point, 4326)`) with `id`, `location`, `power_w`, `model`, `status`.
- `bins`: point features with `id`, `location`, `capacity_l`, `type`, `status`.
- `bin_telemetry`: telemetry records, FK `bin_id`, fields `level_pct`, `temperature`, `battery`, `timestamp`.
- `lamp_issues`: reported lamp issues, FK `lamp_id`, fields `issue_type`, `severity`, `description`, `reported_at`, `resolved_at`, `status`.
- `bin_issues`: analogous to lamp issues, FK `bin_id`.
- Indexing: spatial index on `geom` for greens/lamps/bins; temporal index on `bin_telemetry.timestamp`.

## Security
- Bin telemetry API protected by **scoped API tokens**:
  - Table `api_tokens` holds token hash, scope, expiration, last_used, enabled.
  - Telemetry endpoints (`/api/v1/telemetry/bins`) require `X-API-Key`.
  - Apply rate limiting (Traefik middleware or a FastAPI limiter).
  - Logging/audit: store `token_id`, IP, user-agent.
- Application API for the frontend can use JWT/OAuth2 with scopes `read`, `write`, `admin`.
- HTTPS enforced at the proxy; enable HSTS there, keep CORS strict, and use secure cookies if applicable.

## Deployment steps
1. Build the `frontend` Docker image (npm build → nginx).
2. Build the `backend` Docker image (uvicorn/gunicorn).
3. Run `docker-compose up` or deploy to K8s; Traefik/Nginx exposes ports 80/443.
4. Run migrations (`alembic upgrade head`).
5. Run geo import jobs as needed.
6. Frontend talks to backend via the `/api` proxy; all traffic is HTTPS.

## Testing
⚠️ Tests not run (documentation-only change).
