"""Tests for provider-independent, evidence-grounded answer orchestration."""

import json
from pathlib import Path

from mirage.knowledge.answering import AnswerStatus, answer_question
from mirage.knowledge.indexing import SQLiteKnowledgeStore
from mirage.knowledge.pipeline import ingest_markdown_file
from mirage.knowledge.retrieval import retrieve

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = "data/test_sources/animal_kingdom_300_words.md"


class FakeGenerator:
    def __init__(self, payload_factory):
        self.payload_factory = payload_factory
        self.called = False

    def generate(self, question, evidence):
        self.called = True
        return json.dumps(self.payload_factory(evidence))


def test_answer_uses_only_retrieved_chunk_ids(tmp_path):
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        ingest_markdown_file(ROOT, FIXTURE, store)
        hits = retrieve("birds feathers beaks", store)
        assert hits
        expected_id = hits[0].chunk.chunk_id
        generator = FakeGenerator(
            lambda evidence: {
                "answer": "Birds have feathers and beaks.",
                "citation_chunk_ids": [expected_id],
            }
        )

        answer = answer_question("What do birds have?", store, generator)

        assert generator.called
        assert answer.status is AnswerStatus.ANSWERED
        assert answer.text == "Birds have feathers and beaks."
        assert answer.citations[0].chunk_id == expected_id
        assert answer.citations[0].source_locator == FIXTURE


def test_unknown_citation_is_rejected(tmp_path):
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        ingest_markdown_file(ROOT, FIXTURE, store)
        generator = FakeGenerator(
            lambda evidence: {
                "answer": "Unsupported claim.",
                "citation_chunk_ids": ["not-a-retrieved-chunk"],
            }
        )

        answer = answer_question("What do birds have?", store, generator)

        assert answer.status is AnswerStatus.INSUFFICIENT_EVIDENCE
        assert answer.citations == ()


def test_no_retrieval_abstains_without_calling_generator(tmp_path):
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        ingest_markdown_file(ROOT, FIXTURE, store)
        generator = FakeGenerator(lambda evidence: {})

        answer = answer_question("xylophone quantum nebula", store, generator)

        assert answer.status is AnswerStatus.INSUFFICIENT_EVIDENCE
        assert not generator.called


def test_malformed_generator_output_abstains(tmp_path):
    class BrokenGenerator:
        def generate(self, question, evidence):
            return "not json"

    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        ingest_markdown_file(ROOT, FIXTURE, store)
        answer = answer_question("What do birds have?", store, BrokenGenerator())

        assert answer.status is AnswerStatus.INSUFFICIENT_EVIDENCE
