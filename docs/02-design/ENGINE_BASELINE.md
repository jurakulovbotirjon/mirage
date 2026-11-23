# Mirage Engine Baseline

**Status:** Implemented deterministic baseline  
**Purpose:** Establish measurable, source-grounded behavior before introducing a generative model.

## What the engine currently is

The first runnable answer engine is extractive. It does not call an LLM, use a hosted provider, or generate new factual sentences. It selects complete sentences from retrieved source chunks and returns the chunk identifiers that supplied those sentences.

This is intentional: it gives us a real baseline whose output can be checked exactly against its source. It is not being presented as a conversational LLM.

## Runtime flow

1. A question enters the answer service.
2. The SQLite FTS5 retriever finds relevant source chunks.
3. If retrieval finds nothing, Mirage returns `insufficient_evidence` without invoking an answer engine.
4. The extractive engine tokenizes the question and candidate sentences, scores lexical overlap, and selects up to two complete source sentences.
5. It returns the selected text and the exact chunk IDs in the existing generator JSON contract.
6. The answer service verifies that every cited ID belongs to the retrieved set and maps it back to source provenance and character offsets.
7. If there is insufficient overlap, malformed output, or an unknown citation, Mirage abstains.

## What this can and cannot prove

**It can demonstrate:**
- source ingestion and retrieval are connected to answer generation;
- a supported question can receive a verbatim answer from indexed text;
- the answer is linked to a real source locator and chunk;
- unrelated or weak evidence leads to abstention;
- the engine cannot invent a new sentence because it only selects source sentences.

**It cannot demonstrate:**
- broad world knowledge or general reasoning;
- semantic understanding beyond lexical overlap;
- that a retrieved passage logically entails every possible interpretation of a question;
- natural, synthesized conversational answers.

## Why this comes before an LLM

A model can produce fluent nonsense. Before adding one, Mirage needs a measurable baseline and tests that expose retrieval and grounding failures. A later generative adapter must pass the same source-grounding contract plus stronger semantic-entailment and adversarial evaluations.

## Test command

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
ruff format --check .
```

The engine tests cover a supported bird question, insufficient evidence, verbatim-only output, source citations, and invalid configuration.
