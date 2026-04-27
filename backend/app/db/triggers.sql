-- Setup dbgit staging schema
CREATE SCHEMA IF NOT EXISTS dbgit_staging;

-- Table to store pending changes captured by the trigger
CREATE TABLE IF NOT EXISTS dbgit_staging.pending_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payload JSONB NOT NULL,
    session_id TEXT,
    captured_at TIMESTAMPTZ DEFAULT NOW()
);

-- Function to capture changes
CREATE OR REPLACE FUNCTION dbgit_capture_change()
RETURNS TRIGGER AS $$
DECLARE
    change_payload JSONB;
    current_session TEXT;
BEGIN
    -- Try to get the session ID if set by the application, else use a random one or generic
    BEGIN
        current_session := current_setting('dbgit.session_id', TRUE);
    EXCEPTION WHEN undefined_object THEN
        current_session := 'unknown_session';
    END;

    -- Build the change event payload
    change_payload := jsonb_build_object(
        'operation', TG_OP,
        'table_name', TG_TABLE_NAME,
        'schema_name', TG_TABLE_SCHEMA,
        'row_pk', CASE
            WHEN TG_OP IN ('UPDATE', 'DELETE') THEN
                -- Simplistic assumption: we capture the whole row as PK for now or assume an 'id' column exists.
                -- For a generic solution, we should dynamically extract the primary key.
                -- In Phase 1 MVP, we will assume table has 'id' column.
                jsonb_build_object('id', COALESCE(OLD.id::text, 'unknown'))
            ELSE
                jsonb_build_object('id', COALESCE(NEW.id::text, 'unknown'))
        END,
        'before_state', CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        'after_state', CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        'timestamp', NOW()
    );

    -- Push to staging table
    INSERT INTO dbgit_staging.pending_changes (payload, session_id)
    VALUES (change_payload, current_session);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Usage:
-- To track a table:
-- CREATE TRIGGER trg_dbgit_capture_users
-- AFTER INSERT OR UPDATE OR DELETE ON public.users
-- FOR EACH ROW EXECUTE FUNCTION dbgit_capture_change();
