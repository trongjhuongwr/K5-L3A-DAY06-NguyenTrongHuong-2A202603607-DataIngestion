"""PostgreSQL + pgvector persistent store with metadata filtering."""
import os
import json
import psycopg
from typing import Optional, Any
from .models import Chunk


def to_vector_str(emb: list[float]) -> str:
    """Format float list to PostgreSQL vector literal string format: '[x,y,z]'."""
    return f"[{','.join(str(float(x)) for x in emb)}]"


class PgVectorStore:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL is required to connect to pgvector.")

    def init_table(self, table_name: str, dimension: int = 1536) -> None:
        """Create extension and destination table; ensure idempotent recreation."""
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        chunk_id TEXT PRIMARY KEY,
                        document_id TEXT,
                        source TEXT,
                        page INT,
                        content TEXT,
                        metadata JSONB,
                        embedding vector({dimension})
                    );
                """)
                # Clear previous run data for reproducible benchmarks
                cur.execute(f"TRUNCATE TABLE {table_name};")
            conn.commit()

    def insert_chunks(self, table_name: str, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Insert chunks and embeddings with idempotent ON CONFLICT updates."""
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch.")

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                for chunk, emb in zip(chunks, embeddings):
                    v_str = to_vector_str(emb)
                    cur.execute(
                        f"""
                        INSERT INTO {table_name} (chunk_id, document_id, source, page, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s::vector)
                        ON CONFLICT (chunk_id) DO UPDATE 
                        SET content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding;
                        """,
                        (
                            chunk.chunk_id,
                            chunk.document_id,
                            chunk.source,
                            chunk.page,
                            chunk.text,
                            json.dumps(chunk.metadata),
                            v_str
                        )
                    )
            conn.commit()

    def search(
        self,
        table_name: str,
        query_embedding: list[float],
        top_k: int = 3,
        metadata_filter: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """Search top-k nearest chunks using cosine distance, optionally applying metadata filtering."""
        v_str = to_vector_str(query_embedding)
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                if metadata_filter:
                    cur.execute(
                        f"""
                        SELECT chunk_id, document_id, source, page, content, metadata,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM {table_name}
                        WHERE metadata @> %s::jsonb
                        ORDER BY embedding <=> %s::vector ASC
                        LIMIT %s;
                        """,
                        (v_str, json.dumps(metadata_filter), v_str, top_k)
                    )
                else:
                    cur.execute(
                        f"""
                        SELECT chunk_id, document_id, source, page, content, metadata,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM {table_name}
                        ORDER BY embedding <=> %s::vector ASC
                        LIMIT %s;
                        """,
                        (v_str, v_str, top_k)
                    )

                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "chunk_id": r[0],
                        "document_id": r[1],
                        "source": r[2],
                        "page": r[3],
                        "content": r[4],
                        "metadata": r[5],
                        "score": round(float(r[6]), 4)
                    })
                return results
