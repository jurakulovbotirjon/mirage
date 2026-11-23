"""Tests for the core knowledge data contracts."""

import pytest

from mirage.knowledge.models import Document, SourceReference, TextChunk

VALID_SHA256 = "a" * 64


@pytest.fixture
def source() -> SourceReference:
    return SourceReference(
        source_id="animal-kingdom-300-words",
        title="Animal Kingdom Test Source",
        locator="data/test_sources/animal_kingdom_300_words.md",
        sha256=VALID_SHA256,
    )


def test_source_reference_preserves_provenance(source: SourceReference) -> None:
    assert source.locator.endswith("animal_kingdom_300_words.md")
    assert source.sha256 == VALID_SHA256


def test_source_reference_rejects_invalid_checksum() -> None:
    with pytest.raises(ValueError, match="sha256"):
        SourceReference("source", "Title", "source.md", "not-a-checksum")


def test_document_requires_nonempty_text(source: SourceReference) -> None:
    with pytest.raises(ValueError, match="document text"):
        Document("animal-doc", "  ", source)


def test_chunk_validates_offsets(source: SourceReference) -> None:
    chunk = TextChunk(
        chunk_id="animal-doc:chunk:0",
        document_id="animal-doc",
        source=source,
        text="Fish have gills.",
        chunk_index=0,
        start_char=0,
        end_char=len("Fish have gills."),
    )
    assert chunk.end_char - chunk.start_char == len(chunk.text)


def test_chunk_rejects_mismatched_offsets(source: SourceReference) -> None:
    with pytest.raises(ValueError, match="offsets"):
        TextChunk(
            chunk_id="animal-doc:chunk:0",
            document_id="animal-doc",
            source=source,
            text="Fish have gills.",
            chunk_index=0,
            start_char=0,
            end_char=3,
        )
