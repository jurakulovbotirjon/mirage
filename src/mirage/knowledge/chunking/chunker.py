"""Deterministic character-based chunking with source-offset preservation."""

from __future__ import annotations

from mirage.knowledge.models import Document, TextChunk


def chunk_document(
    document: Document, *, max_chars: int = 500, overlap_chars: int = 50
) -> list[TextChunk]:
    """Split a document into reproducible, overlapping text chunks.

    Chunk boundaries prefer whitespace so words are not split unnecessarily.
    Every returned text value is an exact slice of the original document, and
    start_char/end_char identify that slice using half-open offsets.

    A single token longer than max_chars is kept intact rather than split.
    """
    if max_chars < 1:
        raise ValueError("max_chars must be at least 1")
    if overlap_chars < 0:
        raise ValueError("overlap_chars cannot be negative")
    if overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be smaller than max_chars")

    text = document.text
    chunks: list[TextChunk] = []
    cursor = 0

    while cursor < len(text):
        # Ignore whitespace between passages; offsets still point into source.
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor >= len(text):
            break

        proposed_end = min(cursor + max_chars, len(text))
        end = proposed_end

        if proposed_end < len(text):
            # Prefer the last whitespace boundary within the size limit.
            boundary = max(
                text.rfind(" ", cursor + 1, proposed_end + 1),
                text.rfind("\n", cursor + 1, proposed_end + 1),
                text.rfind("\t", cursor + 1, proposed_end + 1),
                text.rfind("\r", cursor + 1, proposed_end + 1),
            )
            if boundary > cursor:
                end = boundary
            else:
                # The first token itself exceeds max_chars. Preserve the whole
                # token by extending to its next whitespace boundary.
                next_boundaries = [
                    position
                    for separator in (" ", "\n", "\t", "\r")
                    if (position := text.find(separator, proposed_end)) != -1
                ]
                end = min(next_boundaries) if next_boundaries else len(text)

        # Do not emit empty chunks if a boundary falls directly at the cursor.
        if end <= cursor:
            end = proposed_end

        chunk_text = text[cursor:end].rstrip()
        actual_end = cursor + len(chunk_text)
        if chunk_text:
            index = len(chunks)
            chunks.append(
                TextChunk(
                    chunk_id=f"{document.document_id}:chunk:{index:04d}",
                    document_id=document.document_id,
                    source=document.source,
                    text=chunk_text,
                    chunk_index=index,
                    start_char=cursor,
                    end_char=actual_end,
                )
            )

        if actual_end >= len(text):
            break

        # Move backwards by the requested overlap, then skip whitespace at
        # the next iteration. The max(cursor + 1, ...) guard guarantees progress.
        cursor = max(cursor + 1, actual_end - overlap_chars)

    return chunks
