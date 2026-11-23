"""Immutable result contracts for evidence-grounded answers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True, slots=True)
class Citation:
    """A reference to a retrieved knowledge chunk."""

    chunk_id: str
    source_id: str
    source_title: str
    source_locator: str
    start_char: int
    end_char: int

    def __post_init__(self) -> None:
        for name in ("chunk_id", "source_id", "source_title", "source_locator"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        if self.start_char < 0 or self.end_char <= self.start_char:
            raise ValueError("citation offsets must define a positive range")


@dataclass(frozen=True, slots=True)
class Answer:
    """Answer output with explicit evidence status and source citations."""

    question: str
    text: str
    status: AnswerStatus
    citations: tuple[Citation, ...] = ()

    def __post_init__(self) -> None:
        if not self.question.strip():
            raise ValueError("question must not be empty")
        if self.status is AnswerStatus.ANSWERED and not self.text.strip():
            raise ValueError("answered results must contain answer text")
        if self.status is AnswerStatus.INSUFFICIENT_EVIDENCE and self.citations:
            raise ValueError("insufficient-evidence results cannot claim citations")
