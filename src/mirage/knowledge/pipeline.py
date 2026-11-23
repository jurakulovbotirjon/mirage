"""Application-level orchestration for the first local knowledge pipeline."""

from __future__ import annotations

from pathlib import Path

from mirage.knowledge.chunking import chunk_document
from mirage.knowledge.indexing import SQLiteKnowledgeStore
from mirage.knowledge.ingestion import load_markdown_source


def ingest_markdown_file(
    repository_root: str | Path,
    relative_path: str,
    store: SQLiteKnowledgeStore,
    *,
    expected_sha256: str | None = None,
    max_chars: int = 500,
    overlap_chars: int = 50,
) -> int:
    """Load, chunk, and index one approved Markdown file; return chunk count."""
    document = load_markdown_source(
        repository_root, relative_path, expected_sha256=expected_sha256
    )
    chunks = chunk_document(
        document, max_chars=max_chars, overlap_chars=overlap_chars
    )
    return store.replace_document_chunks(chunks)
