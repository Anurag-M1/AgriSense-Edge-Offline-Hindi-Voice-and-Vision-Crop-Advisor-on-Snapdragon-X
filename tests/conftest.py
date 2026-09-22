"""
conftest.py — Shared test fixtures for AgriSense Edge.
"""


import numpy as np
import pytest

from app.backend.db import Database
from app.backend.engines.asr import ASREngine
from app.backend.engines.llm import LLMEngine
from app.backend.engines.tts import TTSEngine
from app.backend.engines.vision import VisionEngine
from app.backend.pipeline import Pipeline
from app.backend.retrieval import RetrievalEngine


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary database for testing."""
    db = Database(tmp_path / "test.db")
    db.connect()
    yield db
    db.close()


@pytest.fixture
def asr_engine():
    """Create an ASR engine instance (CPU backend)."""
    engine = ASREngine()
    engine.load("cpu")
    yield engine
    engine.unload()


@pytest.fixture
def vision_engine():
    """Create a vision engine instance (CPU backend)."""
    engine = VisionEngine()
    engine.load("cpu")
    yield engine
    engine.unload()


@pytest.fixture
def llm_engine():
    """Create an LLM engine instance (CPU backend)."""
    engine = LLMEngine()
    engine.load("cpu")
    yield engine
    engine.unload()


@pytest.fixture
def tts_engine():
    """Create a TTS engine instance (CPU backend)."""
    engine = TTSEngine()
    engine.load("cpu")
    yield engine
    engine.unload()


@pytest.fixture
def retrieval_engine(tmp_db):
    """Create a retrieval engine with a temp database."""
    engine = RetrievalEngine(tmp_db)
    engine.load()
    yield engine
    engine.unload()


@pytest.fixture
def test_pipeline(asr_engine, vision_engine, retrieval_engine, llm_engine, tts_engine):
    """Create a full test pipeline with all engines."""
    return Pipeline(asr_engine, vision_engine, retrieval_engine, llm_engine, tts_engine)


@pytest.fixture
def sample_audio():
    """Generate a sample audio waveform (1 second of silence)."""
    return np.zeros(16000, dtype=np.float32)


@pytest.fixture
def sample_image():
    """Generate a sample image (224x224 RGB)."""
    return np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
