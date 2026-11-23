# Source Ingestion Design

**Status:** Initial Markdown loader implemented

## Scope

The first loader handles repository-relative UTF-8 Markdown fixtures. It does not fetch remote URLs, parse PDFs, execute document content, or call an AI model.

## Processing rules

1. Resolve the supplied path and reject paths outside the repository root.
2. Read source bytes without modifying the original file.
3. Calculate SHA-256 over the exact original bytes.
4. Optionally compare the digest with a caller-supplied expected digest.
5. Extract the first Markdown H1 as the title.
6. Skip leading blank and bold metadata lines; preserve the remaining body text.
7. Create an immutable `Document` with a `SourceReference` and checksum-derived document ID.

## Provenance

The source reference stores a stable source ID, title, repository-relative locator, media type, and SHA-256 digest. Any source edit changes the digest and therefore the document ID.

## Security boundaries

The loader only reads local files beneath the configured repository root. It does not follow arbitrary network locations. It treats all file contents as data, never executable instructions.

## Tests

Unit tests cover body extraction, title and checksum provenance, checksum mismatch, path traversal, and missing files.

## Next

Pass the loaded document through deterministic chunking, then persist the resulting chunks in the local SQLite FTS index.
