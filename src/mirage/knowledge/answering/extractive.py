"""Deterministic extractive answer engine for source-grounded baseline tests.

This engine does not invent prose or call a language model. It selects complete
sentences from retrieved source chunks and returns their originating chunk IDs.
It is a real, testable baseline while a generative model remains an explicit,
separately evaluated adapter.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence

_WORD_PATTERN = re.compile(r"[^\W_]+", flags=re.UNICODE)
_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")
_EVIDENCE_PATTERN = re.compile(r"^\[([^\]]+)\]\s*(.*)$", flags=re.DOTALL)
_STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "do", "does",
        "for", "from", "how", "i", "in", "is", "it", "of", "on", "or",
        "the", "their", "there", "these", "they", "this", "those", "to",
        "was", "we", "what", "when", "where", "which", "who", "why",
        "with", "you",
    }
)


def _terms(value: str) -> set[str]:
    """Return normalized content words for simple lexical comparison."""
    return {
        token.casefold()
        for token in _WORD_PATTERN.findall(value)
        if token.casefold() not in _STOPWORDS
    }


class ExtractiveAnswerGenerator:
    """Select source sentences; never synthesize claims beyond supplied text."""

    def __init__(self, *, max_sentences: int = 2) -> None:
        if max_sentences < 1:
            raise ValueError("max_sentences must be at least 1")
        self.max_sentences = max_sentences

    def generate(self, question: str, evidence: Sequence[str]) -> str:
        """Return the service's JSON contract with exact sentence excerpts."""
        query_terms = _terms(question)
        if not query_terms:
            return json.dumps({"answer": "", "citation_chunk_ids": []})

        minimum_overlap = min(2, len(query_terms))
        candidates: list[tuple[int, float, str, str]] = []

        for item in evidence:
            match = _EVIDENCE_PATTERN.match(item)
            if match is None:
                continue
            chunk_id, chunk_text = match.groups()
            for sentence in _SENTENCE_PATTERN.split(chunk_text.strip()):
                sentence = sentence.strip()
                sentence_terms = _terms(sentence)
                overlap = len(query_terms & sentence_terms)
                if overlap < minimum_overlap:
                    continue
                coverage = overlap / len(query_terms)
                candidates.append((overlap, coverage, chunk_id, sentence))

        candidates.sort(
            key=lambda item: (item[0], item[1], -len(item[3])),
            reverse=True,
        )
        selected: list[tuple[str, str]] = []
        seen_sentences: set[str] = set()
        for _, _, chunk_id, sentence in candidates:
            normalized = sentence.casefold()
            if normalized in seen_sentences:
                continue
            selected.append((chunk_id, sentence))
            seen_sentences.add(normalized)
            if len(selected) >= self.max_sentences:
                break

        if not selected:
            return json.dumps({"answer": "", "citation_chunk_ids": []})

        return json.dumps(
            {
                "answer": " ".join(sentence for _, sentence in selected),
                "citation_chunk_ids": list(dict.fromkeys(chunk_id for chunk_id, _ in selected)),
            }
        )
