"""PostgreSQL storage scoped to one anonymous demo browser."""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID, uuid4

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


class DatabaseNotConfigured(RuntimeError):
    """The app has no database connection string yet."""


@contextmanager
def _connection() -> Iterator[psycopg.Connection]:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise DatabaseNotConfigured("DATABASE_URL ist nicht gesetzt.")
    with psycopg.connect(url, row_factory=dict_row) as connection:
        yield connection


def _touch_session(connection: psycopg.Connection, session_id: str) -> None:
    """Expire idle demo data, then create or refresh this visitor's session."""
    connection.execute(
        "DELETE FROM demo_sessions WHERE last_seen_at < now() - interval '24 hours'"
    )
    connection.execute(
        """
        INSERT INTO demo_sessions (id) VALUES (%s)
        ON CONFLICT (id) DO UPDATE SET last_seen_at = now()
        """,
        (session_id,),
    )


def save_document(
    session_id: str,
    filename: str,
    pages: list[dict[str, str | int]],
    chunks: list[dict[str, str | int]],
) -> str:
    """Store one visitor's document and page-aware passages atomically."""
    document_id = str(uuid4())
    with _connection() as connection:
        _touch_session(connection, session_id)
        connection.execute(
            """
            INSERT INTO documents (id, session_id, filename, page_count)
            VALUES (%s, %s, %s, %s)
            """,
            (document_id, session_id, filename, len(pages)),
        )
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO chunks (document_id, page_number, chunk_number, content)
                VALUES (%s, %s, %s, %s)
                """,
                [
                    (
                        document_id,
                        chunk["seitenzahl"],
                        chunk["abschnitt_nummer"],
                        chunk["text"],
                    )
                    for chunk in chunks
                ],
            )
    return document_id


def list_documents(session_id: str) -> list[dict]:
    """List only documents owned by this browser's session."""
    with _connection() as connection:
        _touch_session(connection, session_id)
        return connection.execute(
            """
            SELECT id, filename, page_count, created_at
            FROM documents
            WHERE session_id = %s
            ORDER BY created_at DESC, id DESC
            """,
            (session_id,),
        ).fetchall()


def get_document_chunks(session_id: str, document_id: UUID) -> list[dict]:
    """Return source passages only when the document belongs to this visitor."""
    with _connection() as connection:
        _touch_session(connection, session_id)
        return connection.execute(
            """
            SELECT d.filename, c.page_number, c.chunk_number, c.content
            FROM documents AS d
            JOIN chunks AS c ON c.document_id = d.id
            WHERE d.session_id = %s AND d.id = %s
            ORDER BY c.page_number, c.chunk_number
            """,
            (session_id, document_id),
        ).fetchall()
