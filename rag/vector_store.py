from typing import Iterable, List, Tuple

import psycopg
from pgvector.psycopg import register_vector

from app.config import get_settings


TABLE_NAME = "policy_chunks"


def _connect() -> psycopg.Connection:
    settings = get_settings()
    conn = psycopg.connect(settings.database_url, autocommit=True)
    return conn


def init_schema() -> None:
    settings = get_settings()
    dim = settings.embedding_dim

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    chunk_index INT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector({dim}) NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb
                );
                """
            )
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {TABLE_NAME}_embedding_idx
                ON {TABLE_NAME}
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
                """
            )

            cur.execute(
                """
                SELECT atttypmod
                FROM pg_attribute
                WHERE attrelid = %s::regclass AND attname = 'embedding'
                """,
                (TABLE_NAME,),
            )
            row = cur.fetchone()
            if row and row[0] not in (None, dim):
                print(
                    f"[vector_store] WARNING: existing embedding column has dim {row[0]}, "
                    f"but EMBEDDING_DIM={dim}. Drop the table to recreate."
                )


def upsert_chunks(
    rows: Iterable[Tuple[str, str, int, str, List[float], dict]],
) -> int:
    count = 0
    with _connect() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            for doc_id, source, chunk_index, content, embedding, metadata in rows:
                cur.execute(
                    f"""
                    INSERT INTO {TABLE_NAME} (id, source, chunk_index, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET source = EXCLUDED.source,
                        chunk_index = EXCLUDED.chunk_index,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata;
                    """,
                    (doc_id, source, chunk_index, content, embedding, psycopg.types.json.Jsonb(metadata)),
                )
                count += 1
    return count


def query_top_k(query_embedding: List[float], k: int = 4):
    with _connect() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, source, chunk_index, content, metadata,
                       embedding <=> %s::vector AS distance
                FROM {TABLE_NAME}
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (query_embedding, query_embedding, k),
            )
            return cur.fetchall()
