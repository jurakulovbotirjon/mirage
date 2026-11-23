# Deterministic Chunking Design

**Status:** Implemented initial chunker

## Responsibility

Convert one normalized `Document` into ordered `TextChunk` records. The chunker does not read files, modify source text, create embeddings, persist data, or answer questions.

## Algorithm

1. Validate that the maximum chunk size is positive and overlap is non-negative and smaller than the maximum.
2. Start at the next non-whitespace character.
3. Select a boundary no longer than the configured maximum, preferring the last whitespace boundary.
4. Store the exact source slice and its half-open character offsets.
5. Move the next start backward by the configured overlap, then skip leading whitespace.
6. Generate an ordered chunk ID from the document ID and zero-based chunk index.

An unbroken token longer than the configured maximum is kept intact rather than split. This preserves token integrity, so such a chunk may exceed the nominal maximum.

## Guarantees

- Repeatable output for identical document text and settings.
- Each chunk points to the same source reference as its parent document.
- Each chunk text equals `document.text[start_char:end_char]`.
- Chunk order is explicit and zero-based.
- Overlap is measured in characters and is approximate when whitespace is skipped.

## Initial defaults

- `max_chars=500`
- `overlap_chars=50`

These are starting defaults for the small controlled text corpus, not universal values. They can be tuned after retrieval evaluation.

## Tests

Unit tests cover short input, multiple chunks, exact offsets, overlap, determinism, invalid configuration, whitespace-only input, and long unbroken tokens.

## Next step

Implement source loading and checksum verification so the existing Markdown test source becomes a `Document` without losing its provenance.
