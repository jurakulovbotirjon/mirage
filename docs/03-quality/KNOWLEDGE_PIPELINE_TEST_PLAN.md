# Knowledge Pipeline Test Plan

**Status:** Initial automated test suite added

## Scope

Validate the first local knowledge path from source file to retrieved passage:

`Markdown source → checksum verification → Document → TextChunk[] → SQLite FTS5 → RetrievalHit[]`

## Test layers

### Unit tests

- Source checksum and provenance are recorded correctly.
- Invalid checksums and paths outside the repository root are rejected.
- Document and chunk invariants are enforced.
- Chunking is deterministic and preserves exact character offsets.
- SQLite writes replace a document atomically and preserve chunk counts.
- Retrieval handles empty queries, invalid limits, and source traceability.

### Integration tests

- The animal kingdom fixture can be ingested into a temporary SQLite database.
- A question about feathers and beaks retrieves the relevant bird passage.
- The source locator is preserved in the retrieval result.
- A query containing unrelated terms returns no matches.

## Continuous integration

GitHub Actions runs the test suite on Python 3.11 and 3.13 for pushes to main, pull requests, and manual dispatch.

## Acceptance boundary

Passing retrieval tests proves only that the system can find source passages. It does not prove that an LLM can formulate faithful answers. Answer generation, citation enforcement, and refusal behavior belong to a later milestone.
