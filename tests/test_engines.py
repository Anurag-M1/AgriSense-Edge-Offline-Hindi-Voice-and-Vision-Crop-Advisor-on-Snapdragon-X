"""
test_engines.py — Unit tests for AgriSense Edge inference engines.
"""

import numpy as np
import pytest

from app.backend.engines.asr import ASREngine
from app.backend.engines.base import EngineBase
from app.backend.engines.llm import LLMEngine
from app.backend.engines.tts import TTSEngine
from app.backend.engines.vision import VisionEngine


class TestEngineBase:
    """Test the abstract engine base class."""

    def test_engine_not_loaded_by_default(self, asr_engine):
        """Engines should be loaded after load() is called."""
        engine = ASREngine()
        assert not engine.is_loaded()
        assert engine.backend_name == "none"

    def test_engine_loaded_after_load(self, asr_engine):
        assert asr_engine.is_loaded()
        assert asr_engine.backend_name == "cpu"


class TestASREngine:
    """Test the ASR engine."""

    def test_transcribe_returns_result(self, asr_engine, sample_audio):
        result = asr_engine.transcribe(sample_audio)
        assert result.text is not None
        assert result.language is not None
        assert result.latency_ms >= 0

    def test_transcribe_without_load_raises(self, sample_audio):
        engine = ASREngine()
        with pytest.raises(RuntimeError, match="not loaded"):
            engine.transcribe(sample_audio)


class TestVisionEngine:
    """Test the vision engine."""

    def test_classify_returns_result(self, vision_engine, sample_image):
        result = vision_engine.classify(sample_image)
        assert result.label is not None
        assert result.confidence >= 0
        assert len(result.top_3) > 0
        assert result.latency_ms >= 0

    def test_classify_without_load_raises(self, sample_image):
        engine = VisionEngine()
        with pytest.raises(RuntimeError, match="not loaded"):
            engine.classify(sample_image)

    def test_labels_populated(self, vision_engine):
        assert len(vision_engine.labels) > 0

    def test_confidence_threshold(self, vision_engine):
        assert 0 < vision_engine.confidence_threshold < 1


class TestLLMEngine:
    """Test the LLM engine."""

    def test_generate_returns_result(self, llm_engine):
        result = llm_engine.generate(
            disease_label="Tomato___Early_blight",
            confidence=0.85,
            farmer_question="इस पत्ती में क्या बीमारी है?",
            retrieved_notes=["Test note about early blight"],
        )
        assert result.text is not None
        assert result.total_latency_ms >= 0
        assert result.backend_used == "cpu"

    def test_generate_without_load_raises(self):
        engine = LLMEngine()
        with pytest.raises(RuntimeError, match="not loaded"):
            engine.generate("test", 0.5, "test", [])


class TestTTSEngine:
    """Test the TTS engine."""

    def test_synthesize_returns_result(self, tts_engine):
        result = tts_engine.synthesize("नमस्ते")
        assert result.latency_ms >= 0
        assert result.sample_rate > 0

    def test_synthesize_without_load_raises(self):
        engine = TTSEngine()
        with pytest.raises(RuntimeError, match="not loaded"):
            engine.synthesize("test")
