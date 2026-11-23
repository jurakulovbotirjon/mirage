"""Behavioral tests for Mirage's deterministic answer engine."""

from pathlib import Path

from mirage.knowledge.answering import AnswerStatus, answer_question
from mirage.knowledge.answering.extractive import ExtractiveAnswerGenerator
from mirage.knowledge.indexing import SQLiteKnowledgeStore
from mirage.knowledge.pipeline import ingest_markdown_file

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = "data/test_sources/animal_kingdom_300_words.md"


def test_engine_returns_verbatim_supported_sentence_and_citation(tmp_path):
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        ingest_markdown_file(ROOT, FIXTURE, store)
        answer = answer_question(
            "What do birds have?",
            store,
            ExtractiveAnswerGenerator(),
        )

    assert answer.status is AnswerStatus.ANSWERED
    assert answer.text == "Birds have feathers, beaks, and wings."
    assert len(answer.citations) == 1
    assert answer.citations[0].source_locator == FIXTURE
    assert answer.citations[0].start_char >= 0


def test_engine_abstains_when_retrieved_evidence_has_too_little_overlap():
    engine = ExtractiveAnswerGenerator()
    result = engine.generate(
        "What do birds have?",
        ["[chunk-1] Fish are aquatic vertebrates that breathe through gills."],
    )

    assert '"answer": ""' in result
    assert '"citation_chunk_ids": []' in result


def test_engine_does_not_invent_or_rewrite_source_sentences():
    engine = ExtractiveAnswerGenerator()
    source_sentence = "Birds have feathers, beaks, and wings."
    result = engine.generate(
        "What do birds have?",
        [f"[chunk-bird] {source_sentence}"],
    )

    assert source_sentence in result
    assert "Birds can fly" not in result


def test_engine_rejects_invalid_sentence_limit():
    try:
        ExtractiveAnswerGenerator(max_sentences=0)
    except ValueError as error:
        assert str(error) == "max_sentences must be at least 1"
    else:
        raise AssertionError("expected invalid sentence limit to be rejected")
