"""
test_offline.py — Offline operation proof for AgriSense Edge.

Blocks all network sockets and runs the full pipeline to verify
that no internet is required for any step.
"""

import socket
from unittest.mock import patch

import numpy as np
import pytest


def _block_socket(*args, **kwargs):
    """Replacement for socket.socket that always raises."""
    raise OSError("Network access blocked by test_offline.py")


@pytest.mark.offline
class TestOfflineOperation:
    """Verify that the full pipeline works with networking blocked."""

    def test_pipeline_runs_without_network(self, test_pipeline, sample_audio, sample_image):
        """Block all sockets and run the full pipeline."""
        with patch("socket.socket", side_effect=_block_socket):
            result = test_pipeline.run(
                audio=sample_audio,
                image=sample_image,
                sample_rate=16000,
            )
            # Pipeline should complete without errors
            assert result.total_latency_ms >= 0
            # At least some stages should have run
            assert len(result.stages) > 0

    def test_engines_load_without_network(self):
        """Verify all engines can load without network access."""
        from app.backend.engines.asr import ASREngine
        from app.backend.engines.llm import LLMEngine
        from app.backend.engines.tts import TTSEngine
        from app.backend.engines.vision import VisionEngine

        with patch("socket.socket", side_effect=_block_socket):
            asr = ASREngine()
            asr.load("cpu")
            assert asr.is_loaded()
            asr.unload()

            vision = VisionEngine()
            vision.load("cpu")
            assert vision.is_loaded()
            vision.unload()

            llm = LLMEngine()
            llm.load("cpu")
            assert llm.is_loaded()
            llm.unload()

            tts = TTSEngine()
            tts.load("cpu")
            assert tts.is_loaded()
            tts.unload()

    def test_database_works_without_network(self, tmp_db):
        """Verify database operations work offline."""
        with patch("socket.socket", side_effect=_block_socket):
            case_id = tmp_db.save_case(
                disease_label="Tomato___Early_blight",
                confidence=0.85,
                farmer_question="टमाटर की पत्ती में क्या है?",
                llm_response="यह अगेती अंगमारी है।",
                backend_used="cpu",
                latency_ms=1234.5,
            )
            assert case_id is not None
            assert case_id > 0
