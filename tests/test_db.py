"""
test_db.py — Database tests for AgriSense Edge.
"""



class TestDatabase:
    """Test SQLite database operations."""

    def test_save_and_retrieve_case(self, tmp_db):
        case_id = tmp_db.save_case(
            disease_label="Tomato___Early_blight",
            confidence=0.85,
            farmer_question="टमाटर में क्या बीमारी है?",
            llm_response="यह अगेती अंगमारी है।",
            backend_used="cpu",
            latency_ms=1500.0,
        )
        assert case_id is not None
        assert case_id > 0

    def test_save_feedback(self, tmp_db):
        case_id = tmp_db.save_case(
            disease_label="test",
            confidence=0.5,
            farmer_question="test",
            llm_response="test",
            backend_used="cpu",
            latency_ms=100.0,
        )
        tmp_db.save_feedback(case_id, helpful=True, comment="Good advice")

    def test_settings(self, tmp_db):
        tmp_db.set_setting("language", "hi")
        assert tmp_db.get_setting("language") == "hi"

    def test_get_default_setting(self, tmp_db):
        assert tmp_db.get_setting("nonexistent", "default") == "default"

    def test_save_kb_vector(self, tmp_db):
        import numpy as np
        embedding = np.zeros(384, dtype=np.float32)
        entry_id = tmp_db.save_kb_vector(
            source_file="tomato_early_blight.md",
            crop="Tomato",
            disease="Early_blight",
            chunk_text="Test content about early blight",
            embedding=embedding.tobytes(),
        )
        assert entry_id > 0

        rows = tmp_db.get_kb_vectors(crop="Tomato")
        assert len(rows) == 1
        assert rows[0]["crop"] == "Tomato"
