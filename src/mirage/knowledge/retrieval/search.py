"""Lexical retrieval over the local SQLite FTS5 knowledge index."""

from __future__ import annotations

from dataclasses import dataclass
import re

from mirage.knowledge.indexing.sqlite_store import SQLiteKnowledgeStore
from mirage.knowledge.models import SourceReference, TextChunk


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    """A ranked passage with its source provenance and lexical relevance score."""

    chunk: TextChunk
    score: float


def retrieve(
    query: str, store: SQLiteKnowledgeStore, *, limit: int = 5
) -> list[RetrievalHit]:
    """Return matching chunks ranked by SQLite FTS5 relevance.

    Query input is tokenized and quoted before being passed to FTS5, preventing
    raw user text from being interpreted as FTS query syntax.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")
    terms = re.findall(r"[^\W_]+", query, flags=re.UNICODE)
    if not terms:
        return []
    expression = " OR ".join(f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms)
    rows = store._connection.execute(
        """
        SELECT c.*, bm25(knowledge_chunks_fts) AS relevance
        FROM knowledge_chunks_fts AS f
        JOIN knowledge_chunks AS c ON c.chunk_id = f.chunk_id
        WHERE knowledge_chunks_fts MATCH ?
        ORDER BY relevance ASC
        LIMIT ?
        """,
        (expression, limit),
    ).fetchall()

    hits: list[RetrievalHit] = []
    for row in rows:
        source = SourceReference(
            source_id=row["source_id"],
            title=row["source_title"],
            locator=row["source_locator"],
            sha256=row["source_sha256"],
            media_type=row["source_media_type"],
        )
        chunk = TextChunk(
            chunk_id=row["chunk_id"],
            document_id=row["document_id"],
            source=source,
            text=row["chunk_text"],
            chunk_index=row["chunk_index"],
            start_char=row["start_char"],
            end_char=row["end_char"],
        )
        hits.append(RetrievalHit(chunk=chunk, score=float(row["relevance"])))
    return hits
