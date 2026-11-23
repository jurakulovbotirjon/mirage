# Knowledge Pipeline Design

**Status:** Initial contract design
**Milestone:** Source-grounded knowledge foundation

## Purpose

Define the boundaries and data contracts for the first knowledge pipeline. The first input is the controlled test source at `data/test_sources/animal_kingdom_300_words.md`. The pipeline must preserve provenance from original source to retrieved passage.

## Pipeline stages

1. **Source admission:** only reviewed sources enter the corpus. Record source identity, title, locator, checksum, media type, and license/provenance separately.
2. **Reading and normalization:** read the admitted file and produce a `Document`. Do not rewrite or summarize the source text during ingestion.
3. **Chunking:** split document text into contiguous passages. Each `TextChunk` retains its document ID, source reference, chunk order, and character offsets into the normalized document.
4. **Indexing:** persist chunks and build a searchable index. Indexes are derived artifacts and must be rebuildable.
5. **Retrieval:** return ranked chunks, not unsupported free-form claims. A later answer layer may use retrieved passages and must cite their source references.

## Initial Python contracts

Implemented in `src/mirage/knowledge/models.py`:

- `SourceReference`: source identity and SHA-256 provenance.
- `Document`: non-empty normalized text tied to one source.
- `TextChunk`: non-empty contiguous text with validated character offsets and a stable position within its document.

The models are immutable dataclasses. They contain no file-system, database, network, model-provider, or UI dependencies.

## Invariants

- A source checksum is exactly 64 lowercase hexadecimal characters.
- Document and chunk text cannot be empty or whitespace-only.
- Chunk indices start at zero.
- Chunk offsets are a positive half-open range: `[start_char, end_char)`.
- The offset range length must equal the chunk text length.
- A chunk always carries the source reference from which it originated.

## Deliberately deferred

The first contract layer does not choose a vector database, embedding model, PDF parser, API framework, or hosted service. Those decisions require a demonstrated need and separate design review. The first implementation will use the existing plain-text Markdown fixture and deterministic local processing.

## Next implementation slice

Implement a deterministic chunker that accepts a `Document`, produces ordered `TextChunk` records, preserves exact text offsets, and has unit tests for boundaries, whitespace, and repeatability.
