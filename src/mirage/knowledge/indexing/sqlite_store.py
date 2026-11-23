"""Local SQLite persistence and full-text indexing for knowledge chunks."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from collections.abc import Iterable

from mirage.knowledge.models import SourceReference, TextChunk


class SQLiteKnowledgeStore:
    """Persist chunks and index their text with SQLite FTS5."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        try:
            self._connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_title TEXT NOT NULL,
                    source_locator TEXT NOT NULL,
                    source_sha256 TEXT NOT NULL,
                    source_media_type TEXT NOT NULL,
                    chunk_text TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document
                    ON knowledge_chunks(document_id);
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts
                    USING fts5(chunk_id UNINDEXED, chunk_text);
                """
            )
        except sqlite3.OperationalError as exc:
            self._connection.close()
            raise RuntimeError(
                "This Python SQLite build must include the FTS5 extension"
            ) from exc

    def replace_document_chunks(self, chunks: Iterable[TextChunk]) -> int:
        """Atomically replace all indexed chunks belonging to one document."""
        items = list(chunks)
        if not items:
            raise ValueError("at least one chunk is required")
        document_ids = {item.document_id for item in items}
        if len(document_ids) != 1:
            raise ValueError("all chunks must belong to the same document")

        document_id = items[0].document_id
        rows = [
            (
                item.chunk_id,
                item.document_id,
                item.source.source_id,
                item.source.title,
                item.source.locator,
                item.source.sha256,
                item.source.media_type,
                item.text,
                item.chunk_index,
                item.start_char,
                item.end_char,
            )
            for item in items
        ]
        with self._connection:
            self._connection.execute(
                "DELETE FROM knowledge_chunks_fts WHERE chunk_id IN "
                "(SELECT chunk_id FROM knowledge_chunks WHERE document_id = ?)",
                (document_id,),
            )
            self._connection.execute(
                "DELETE FROM knowledge_chunks WHERE document_id = ?", (document_id,)
            )
            self._connection.executemany(
                """
                INSERT INTO knowledge_chunks VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            self._connection.executemany(
                "INSERT INTO knowledge_chunks_fts(chunk_id, chunk_text) VALUES (?, ?)",
                [(item.chunk_id, item.text) for item in items],
            )
        return len(items)

    def count_chunks(self) -> int:
        row = self._connection.execute(
            "SELECT COUNT(*) AS count FROM knowledge_chunks"
        ).fetchone()
        return int(row["count"])

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> SQLiteKnowledgeStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
