"""End-to-end tests for ingestion, chunking, indexing, and retrieval."""

from pathlib import Path

from mirage.knowledge.indexing import SQLiteKnowledgeStore
from mirage.knowledge.pipeline import ingest_markdown_file
from mirage.knowledge.retrieval import retrieve


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = "data/test_sources/animal_kingdom_300_words.md"


def test_animal_fixture_can_be_ingested_and_retrieved(tmp_path) -> None:
    database = tmp_path / "knowledge.sqlite3"
    with SQLiteKnowledgeStore(database) as store:
        chunk_count = ingest_markdown_file(
            REPOSITORY_ROOT, FIXTURE, store, max_chars=240, overlap_chars=30
        )
        assert chunk_count > 1
        assert store.count_chunks() == chunk_count

        hits = retrieve("Which animals have feathers and beaks?", store, limit=3)
        assert hits
        assert any("Birds have feathers" in hit.chunk.text for hit in hits)
        assert hits[0].chunk.source.locator == FIXTURE


def test_unknown_terms_return_no_results(tmp_path) -> None:
    with SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3") as store:
        ingest_markdown_file(REPOSITORY_ROOT, FIXTURE, store)
        assert retrieve("xylophone quantum nebula", store) == []
