"""Core immutable data contracts for source-grounded knowledge.

These models describe provenance and text boundaries. They deliberately do
not perform file I/O, chunking, indexing, retrieval, or answer generation.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Identify an original source and preserve its provenance."""

    source_id: str
    title: str
    locator: str
    sha256: str
    media_type: str = "text/markdown"

    def __post_init__(self) -> None:
        for field_name in ("source_id", "title", "locator", "media_type"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if not _SHA256_PATTERN.fullmatch(self.sha256):
            raise ValueError("sha256 must be a 64-character lowercase hex digest")


@dataclass(frozen=True, slots=True)
class Document:
    """Normalized text extracted from one identified source."""

    document_id: str
    text: str
    source: SourceReference

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty")
        if not self.text.strip():
            raise ValueError("document text must not be empty")


@dataclass(frozen=True, slots=True)
class TextChunk:
    """A contiguous document passage with stable source offsets."""

    chunk_id: str
    document_id: str
    source: SourceReference
    text: str
    chunk_index: int
    start_char: int
    end_char: int

    def __post_init__(self) -> None:
        if not self.chunk_id.strip():
            raise ValueError("chunk_id must not be empty")
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty")
        if not self.text.strip():
            raise ValueError("chunk text must not be empty")
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be zero or greater")
        if self.start_char < 0 or self.end_char <= self.start_char:
            raise ValueError("chunk character offsets must define a positive range")
        if self.end_char - self.start_char != len(self.text):
            raise ValueError("chunk offsets must match the chunk text length")
