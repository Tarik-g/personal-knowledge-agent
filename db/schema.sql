CREATE EXTENSION IF NOT EXISTS vector;

-- The ID is a SHA-256 hash of the private browser cookie, not the cookie itself.
CREATE TABLE IF NOT EXISTS demo_sessions (
    id text PRIMARY KEY CHECK (length(id) = 64),
    created_at timestamptz NOT NULL DEFAULT now(),
    last_seen_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id uuid PRIMARY KEY,
    session_id text NOT NULL REFERENCES demo_sessions(id) ON DELETE CASCADE,
    filename text NOT NULL,
    page_count integer NOT NULL CHECK (page_count > 0),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS documents_session_id_idx
    ON documents (session_id);

CREATE TABLE IF NOT EXISTS chunks (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number integer NOT NULL CHECK (page_number > 0),
    chunk_number integer NOT NULL CHECK (chunk_number > 0),
    content text NOT NULL,
    embedding vector(384),
    UNIQUE (document_id, page_number, chunk_number)
);

CREATE INDEX IF NOT EXISTS chunks_document_id_idx
    ON chunks (document_id);
