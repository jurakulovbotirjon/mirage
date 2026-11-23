"""Tests for local SQLite chunk persistence and indexing."""

import pytest

from mirage.knowledge.indexing import SQLiteKnowledgeStore
from mirage.knowledge.models import SourceReference, TextChunk


@pytest.fixture
def source() -> SourceReference:
    return SourceReference("source", "Test Source", "test.md", "c" * 64)


def make_chunk(source: SourceReference, index: int, text: str) -> TextChunk:
    return TextChunk(
        chunk_id=f"doc:chunk:{index:04d}",
        document_id="doc",
        source=source,
        text=text,
        chunk_index=index,
        start_char=index * 20,
        end_char=index * 20 + len(text),
    )


def test_store_persists_chunks_and_counts_them(tmp_path, source) -> None:
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        count = store.replace_document_chunks(
            [make_chunk(source, 0, "Fish have gills.")]
        )
        assert count == 1
        assert store.count_chunks() == 1


def test_store_replaces_existing_document_chunks(tmp_path, source) -> None:
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        store.replace_document_chunks([make_chunk(source, 0, "Old passage.")])
        store.replace_document_chunks(
            [
                make_chunk(source, 0, "New passage one."),
                make_chunk(source, 1, "New passage two."),
            ]
        )
        assert store.count_chunks() == 2


def test_store_rejects_empty_or_mixed_documents(source, tmp_path) -> None:
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        with pytest.raises(ValueError, match="at least one"):
            store.replace_document_chunks([])
        other = TextChunk(
            "other:chunk:0", "other", source, "Other text", 0, 0, 10
        )
        with pytest.raises(ValueError, match="same document"):
            store.replace_document_chunks(
                [make_chunk(source, 0, "One."), other]
            )
