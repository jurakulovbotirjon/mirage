"""Unit tests for safe query handling and retrieval boundaries."""

import pytest

from mirage.knowledge.indexing import SQLiteKnowledgeStore
from mirage.knowledge.models import SourceReference, TextChunk
from mirage.knowledge.retrieval import retrieve


def test_retrieve_returns_no_hits_for_empty_query(tmp_path) -> None:
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        assert retrieve("   !!! ", store) == []


def test_retrieve_rejects_nonpositive_limit(tmp_path) -> None:
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        with pytest.raises(ValueError, match="limit"):
            retrieve("fish", store, limit=0)


def test_retrieve_returns_source_traceability(tmp_path) -> None:
    source = SourceReference("fish-source", "Fish Notes", "fish.md", "d" * 64)
    chunk = TextChunk("doc:chunk:0000", "doc", source, "Fish breathe with gills.", 0, 0, 24)
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        store.replace_document_chunks([chunk])
        hits = retrieve("gills", store)
        assert len(hits) == 1
        assert hits[0].chunk.source.source_id == "fish-source"
        assert hits[0].chunk.text == chunk.text
