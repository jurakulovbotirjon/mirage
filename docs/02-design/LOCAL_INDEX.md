# Local Storage and Indexing Design

**Status:** Initial SQLite FTS5 store implemented

## Decision

Use the Python standard-library SQLite driver and SQLite FTS5 for the first local corpus. This keeps the first milestone offline, reproducible, and free of runtime third-party dependencies.

## Data model

The relational `knowledge_chunks` table stores chunk text, stable IDs, document identity, source provenance, chunk order, and source character offsets. The FTS5 virtual table indexes chunk text and carries the chunk ID for lookup.

## Update behavior

`replace_document_chunks` replaces one document's chunks in a single SQLite transaction. A failed write rolls back rather than leaving a half-updated document. Re-ingesting a changed source replaces the old document only when the caller targets the same document ID; checksum-derived IDs intentionally distinguish changed source versions.

## Runtime data

Database files belong under `data/runtime/`, which is ignored by Git. They are derived artifacts and can be rebuilt from approved source files.

## Constraints

- FTS5 must be available in the Python SQLite build.
- The first index is lexical full-text search, not semantic/vector search.
- No network service or model API is required.
- Original source files remain unchanged.

## Next

Expose a retrieval API that converts user queries into safe FTS expressions and returns ranked chunks with their original provenance.
