-- PostgreSQL + PostGIS schema for interactive map
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS greens (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    polygon geometry(Polygon, 4326) NOT NULL,
    frequency_days INTEGER NOT NULL CHECK (frequency_days > 0),
    last_mowed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS lamps (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    point geometry(Point, 4326) NOT NULL
);

CREATE TABLE IF NOT EXISTS bins (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    point geometry(Point, 4326) NOT NULL,
    last_fill_level NUMERIC(5,2),
    last_battery_level NUMERIC(5,2),
    last_temperature NUMERIC(5,2),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bin_telemetry (
    id BIGSERIAL PRIMARY KEY,
    bin_id BIGINT NOT NULL REFERENCES bins(id) ON DELETE CASCADE,
    fill_level NUMERIC(5,2),
    battery_level NUMERIC(5,2),
    temperature NUMERIC(5,2),
    at_time TIMESTAMPTZ NOT NULL DEFAULT now()
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'issue_status') THEN
        CREATE TYPE issue_status AS ENUM ('open', 'in_progress', 'resolved');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS lamp_issues (
    id BIGSERIAL PRIMARY KEY,
    lamp_id BIGINT NOT NULL REFERENCES lamps(id) ON DELETE CASCADE,
    status issue_status NOT NULL DEFAULT 'open',
    type TEXT NOT NULL,
    description TEXT,
    reported_by TEXT NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    resolution_note TEXT
);

CREATE TABLE IF NOT EXISTS bin_issues (
    id BIGSERIAL PRIMARY KEY,
    bin_id BIGINT NOT NULL REFERENCES bins(id) ON DELETE CASCADE,
    status issue_status NOT NULL DEFAULT 'open',
    type TEXT NOT NULL,
    description TEXT,
    reported_by TEXT NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    resolution_note TEXT
);

CREATE INDEX IF NOT EXISTS idx_greens_geom ON greens USING GIST (polygon);
CREATE INDEX IF NOT EXISTS idx_lamps_geom ON lamps USING GIST (point);
CREATE INDEX IF NOT EXISTS idx_bins_geom ON bins USING GIST (point);
CREATE INDEX IF NOT EXISTS idx_bin_telemetry_bin_time ON bin_telemetry (bin_id, at_time DESC);
CREATE INDEX IF NOT EXISTS idx_lamp_issues_status ON lamp_issues (status);
CREATE INDEX IF NOT EXISTS idx_bin_issues_status ON bin_issues (status);
