"""
test_retrieval.py — Unit tests for AgriSense Edge Knowledge Base & Retrieval.

Verifies:
1. Indexing all crop-disease markdown files in kb/ into SQLite.
2. Every supported disease label ALWAYS retrieves its own agronomy note first.
3. Every retrieved output includes valid source citations (ICAR/Govt source).
4. Status is explicitly tagged 'needs agronomist review'.
"""

from pathlib import Path

import pytest

from app.backend.db import Database
from app.backend.retrieval import RetrievalEngine

SUPPORTED_TEST_CASES = [
    ("Tomato___Early_blight", "tomato_early_blight.md", "ICAR-IIHR"),
    ("Tomato___Late_blight", "tomato_late_blight.md", "ICAR-IIHR"),
    ("Potato___Early_blight", "potato_early_blight.md", "ICAR-CPRI"),
    ("Potato___Late_blight", "potato_late_blight.md", "ICAR-CPRI"),
    ("Rice___Bacterial_leaf_blight", "rice_bacterial_leaf_blight.md", "ICAR-IIRR"),
    ("Rice___Brown_spot", "rice_brown_spot.md", "ICAR-IIRR"),
    ("Wheat___Leaf_rust", "wheat_leaf_rust.md", "ICAR-IIWBR"),
    ("Maize___Common_rust", "maize_common_rust.md", "ICAR-IIMR"),
    ("Cotton___Bacterial_blight", "cotton_bacterial_blight.md", "ICAR-CICR"),
    ("Chilli___Leaf_curl", "chilli_leaf_curl.md", "ICAR-IISR"),
    ("Groundnut___Early_leaf_spot", "groundnut_early_leaf_spot.md", "ICAR-DGR"),
]


@pytest.fixture
def populated_engine(tmp_path):
    """Create a test database and populate it from the real kb directory."""
    db_path = tmp_path / "test_kb.db"
    db = Database(str(db_path))
    db.connect()
    engine = RetrievalEngine(db=db)
    engine.load()

    kb_dir = Path("kb")
    count = engine.index_knowledge_base(kb_dir)
    assert count >= 11

    yield engine
    db.close()


class TestKnowledgeBaseRetrieval:
    """Test retrieval engine behavior and source citations."""

    @pytest.mark.parametrize("label,expected_file,expected_source", SUPPORTED_TEST_CASES)
    def test_disease_label_always_retrieves_own_note(
        self, populated_engine, label, expected_file, expected_source
    ):
        """Phase 3 Acceptance: A given disease label always retrieves its own note."""
        results = populated_engine.retrieve(disease_label=label, top_k=1)
        assert len(results) > 0

        top_match = results[0]
        assert top_match.source_file == expected_file, (
            f"Expected {expected_file} for label {label}, got {top_match.source_file}"
        )
        assert expected_source in top_match.source_name or expected_source in top_match.citation
        assert top_match.status == "needs agronomist review"

    def test_retrieval_output_cites_sources(self, populated_engine):
        """Verify all retrieved notes contain non-empty citation fields."""
        results = populated_engine.retrieve(disease_label="Tomato___Early_blight", top_k=3)
        for r in results:
            assert len(r.citation) > 0
            assert "Source:" in r.citation
            assert len(r.source_name) > 0

    def test_semantic_retrieval_with_question(self, populated_engine):
        """Verify semantic query retrieves relevant notes with question."""
        results = populated_engine.retrieve(
            disease_label="Rice___Bacterial_leaf_blight",
            question="धान में जीवाणु झुलसा की रोकथाम कैसे करें",
            top_k=2,
        )
        assert len(results) > 0
        assert results[0].source_file == "rice_bacterial_leaf_blight.md"
