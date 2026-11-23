# Grounded Answer Generation

**Status:** Initial implementation
**Milestone:** Knowledge answer orchestration

## Goal

Turn retrieved passages into a proposed answer while retaining source traceability and a clear abstention state. This layer does not select or install a model provider.

## Flow

1. Receive a non-empty user question.
2. Retrieve matching passages from the existing local SQLite FTS5 index.
3. If retrieval returns no passages, return `insufficient_evidence` without invoking a generator.
4. Pass the question and retrieved evidence to an injected `AnswerGenerator` adapter.
5. Parse the adapter's JSON response and validate that every cited chunk ID belongs to the retrieved set.
6. Return an immutable `Answer` with citations mapped back to source IDs, titles, locators, and character offsets.

## Provider boundary

`AnswerGenerator` is a Python protocol. A future adapter may call a local model, a hosted API, or a deterministic fake used by tests. No Hugging Face dependency, model download, credentials, or network access is required by this milestone.

Expected adapter output:

```json
{
  "answer": "Vertebrates have a backbone.",
  "citation_chunk_ids": ["chunk-id-from-evidence"]
}
```

## Safety and limitations

- Unknown chunk IDs are rejected.
- Missing or malformed citations produce `insufficient_evidence`.
- Empty retrieval abstains before generation.
- Citation membership is structural validation only. It does **not** prove that the cited passage entails the answer.
- The generator is instructed by its adapter contract to use only supplied evidence; prompt enforcement and semantic entailment evaluation remain future work.
- The current FTS5 retriever is lexical, not semantic. Queries with no lexical overlap may fail to retrieve relevant passages.

## Next work

Add deterministic tests using a fake generator, then implement and evaluate a real model adapter only after selecting the execution environment and constraints. No provider is assumed in advance.
