# Retrieval Design

**Status:** Initial lexical retrieval implemented

## Approach

The first retrieval implementation uses SQLite FTS5 over locally stored chunk text. Queries are tokenized into Unicode word terms and quoted before being passed to the FTS query parser. Terms are combined with OR so a query can retrieve passages even when not every query word appears in the same chunk.

## Result contract

Each result is a `RetrievalHit` containing the original `TextChunk` and its FTS5 relevance score. The chunk retains source ID, title, locator, checksum, document ID, chunk index, and character offsets.

## Ranking

SQLite's `bm25` rank is sorted ascending; lower values represent stronger matches. This is lexical relevance, not a calibrated probability or semantic similarity score.

## Safety and limitations

- Raw query syntax is not passed directly to FTS5.
- Empty or punctuation-only queries return no results.
- Unsupported queries can return an empty result set.
- Lexical search may miss synonyms and paraphrases.
- Retrieval does not generate answers. An answer layer must only claim facts supported by retrieved evidence.

## End-to-end path

`ingest_markdown_file` coordinates local source loading, deterministic chunking, and transactional indexing. `retrieve` returns ranked, source-traceable passages from the resulting SQLite index.
