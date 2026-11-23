"""Tests for deterministic, source-traceable document chunking."""

import pytest

from mirage.knowledge.chunking.chunker import chunk_document
from mirage.knowledge.models import Document, SourceReference


@pytest.fixture
def source() -> SourceReference:
    return SourceReference(
        source_id="chunk-test",
        title="Chunking Test",
        locator="tests/fixtures/chunking.txt",
        sha256="b" * 64,
    )


def make_document(text: str, source: SourceReference) -> Document:
    return Document("chunk-test-document", text, source)


def test_short_document_produces_one_exact_chunk(source: SourceReference) -> None:
    document = make_document("Fish have gills.", source)
    chunks = chunk_document(document, max_chars=50, overlap_chars=5)
    assert len(chunks) == 1
    assert chunks[0].text == document.text
    assert (chunks[0].start_char, chunks[0].end_char) == (0, len(document.text))


def test_chunks_respect_size_and_preserve_offsets(source: SourceReference) -> None:
    text = "Fish have gills. Birds have feathers. Mammals produce milk."
    document = make_document(text, source)
    chunks = chunk_document(document, max_chars=25, overlap_chars=0)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 25
        assert document.text[chunk.start_char:chunk.end_char] == chunk.text


def test_overlap_preserves_shared_context(source: SourceReference) -> None:
    document = make_document("alpha beta gamma delta epsilon zeta", source)
    chunks = chunk_document(document, max_chars=16, overlap_chars=5)
    assert len(chunks) > 1
    assert chunks[1].start_char < chunks[0].end_char


def test_chunking_is_deterministic(source: SourceReference) -> None:
    document = make_document("one two three four five six", source)
    first = chunk_document(document, max_chars=12, overlap_chars=2)
    second = chunk_document(document, max_chars=12, overlap_chars=2)
    assert first == second


def test_whitespace_only_document_is_rejected_by_document_model(
    source: SourceReference,
) -> None:
    with pytest.raises(ValueError, match="document text"):
        make_document("  \n  ", source)


@pytest.mark.parametrize(
    ("max_chars", "overlap_chars"),
    [(0, 0), (10, -1), (10, 10)],
)
def test_invalid_chunk_settings_are_rejected(
    source: SourceReference, max_chars: int, overlap_chars: int
) -> None:
    document = make_document("some source text", source)
    with pytest.raises(ValueError):
        chunk_document(document, max_chars=max_chars, overlap_chars=overlap_chars)


def test_long_unbroken_token_is_not_split(source: SourceReference) -> None:
    token = "x" * 40
    document = make_document(token, source)
    chunks = chunk_document(document, max_chars=10, overlap_chars=2)
    assert len(chunks) == 1
    assert chunks[0].text == token
