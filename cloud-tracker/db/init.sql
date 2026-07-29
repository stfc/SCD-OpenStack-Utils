-- Cloud Tracker database initialisation
-- PostgreSQL 15+
-- This file runs once when the container is first created.
-- SQLAlchemy create_all() handles subsequent schema management.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Ensure updated_at is auto-managed
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- quota_changes (pre-created so the trigger can be attached)
CREATE TABLE IF NOT EXISTS quota_changes (
    id               SERIAL PRIMARY KEY,
    project_name     VARCHAR(255) NOT NULL,
    quota_type       VARCHAR(100) NOT NULL,
    current_value    INTEGER      NOT NULL,
    requested_value  INTEGER      NOT NULL,
    unit             VARCHAR(50)  NOT NULL DEFAULT '',
    justification    TEXT         NOT NULL,
    requester_name   VARCHAR(255) NOT NULL,
    requester_email  VARCHAR(255) NOT NULL,
    status           VARCHAR(20)  NOT NULL DEFAULT 'pending',
    admin_notes      TEXT,
    processed_by     VARCHAR(255),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_quota_changes_project ON quota_changes(project_name);
CREATE INDEX IF NOT EXISTS ix_quota_changes_email   ON quota_changes(requester_email);
CREATE INDEX IF NOT EXISTS ix_quota_changes_status  ON quota_changes(status);

DROP TRIGGER IF EXISTS trg_quota_changes_updated_at ON quota_changes;
CREATE TRIGGER trg_quota_changes_updated_at
    BEFORE UPDATE ON quota_changes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- db_snapshots
CREATE TABLE IF NOT EXISTS db_snapshots (
    id             SERIAL PRIMARY KEY,
    snapshot_time  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    snapshot_type  VARCHAR(20)  NOT NULL DEFAULT 'scheduled',
    record_count   INTEGER      NOT NULL DEFAULT 0,
    snapshot_data  JSONB        NOT NULL DEFAULT '{}',
    created_by     VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_db_snapshots_time ON db_snapshots(snapshot_time DESC);

-- Grant
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cloudtracker;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cloudtracker;
