"""Provider-independent orchestration for grounded answer generation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from mirage.knowledge.answering.models import Answer, AnswerStatus, Citation
from mirage.knowledge.retrieval.search import RetrievalHit, retrieve
from mirage.knowledge.indexing.sqlite_store import SQLiteKnowledgeStore


class AnswerGenerator(Protocol):
    """Adapter contract for any future local or remote language model."""

    def generate(self, question: str, evidence: Sequence[str]) -> str:
        """Generate a proposed answer using only the supplied evidence."""


def answer_question(
    question: str,
    store: SQLiteKnowledgeStore,
    generator: AnswerGenerator,
    *,
    limit: int = 5,
) -> Answer:
    """Retrieve evidence, ask a generator, and validate citation identifiers.

    The generator must return JSON with `answer` and `citation_chunk_ids` fields.
    This layer validates structure and membership, not whether the cited text
    semantically entails the answer. That requires a separate evaluation layer.
    """
    if not question.strip():
        raise ValueError("question must not be empty")
    hits = retrieve(question, store, limit=limit)
    if not hits:
        return Answer(
            question=question,
            text="I don't have enough information in my knowledge base to answer that.",
            status=AnswerStatus.INSUFFICIENT_EVIDENCE,
        )

    evidence = [
        f"[{hit.chunk.chunk_id}] {hit.chunk.text}" for hit in hits
    ]
    raw = generator.generate(question, evidence)
    payload = _parse_payload(raw)
    answer_text = payload.get("answer")
    cited_ids = payload.get("citation_chunk_ids")
    available = {hit.chunk.chunk_id: hit for hit in hits}

    if not isinstance(answer_text, str) or not answer_text.strip():
        return _insufficient(question)
    if not isinstance(cited_ids, list) or not cited_ids:
        return _insufficient(question)
    if any(not isinstance(item, str) or item not in available for item in cited_ids):
        return _insufficient(question)

    citations = tuple(_citation(available[chunk_id]) for chunk_id in dict.fromkeys(cited_ids))
    return Answer(
        question=question,
        text=answer_text.strip(),
        status=AnswerStatus.ANSWERED,
        citations=citations,
    )


def _parse_payload(raw: str) -> dict[str, object]:
    import json

    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _citation(hit: RetrievalHit) -> Citation:
    chunk = hit.chunk
    return Citation(
        chunk_id=chunk.chunk_id,
        source_id=chunk.source.source_id,
        source_title=chunk.source.title,
        source_locator=chunk.source.locator,
        start_char=chunk.start_char,
        end_char=chunk.end_char,
    )


def _insufficient(question: str) -> Answer:
    return Answer(
        question=question,
        text="I don't have enough verified information to answer that.",
        status=AnswerStatus.INSUFFICIENT_EVIDENCE,
    )
