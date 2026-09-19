"""
asr.py — Automatic Speech Recognition engine for AgriSense Edge.

Wraps Whisper-Small (multilingual) for Hindi speech transcription.
Supports cpu and qnn_npu backends via ONNX Runtime.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.backend.engines.base import BackendType, EngineBase


@dataclass
class TranscriptionResult:
    """Result of speech transcription."""

    text: str
    language: str
    confidence: float
    latency_ms: float


class ASREngine(EngineBase):
    """Whisper-based automatic speech recognition engine."""

    def __init__(self, model_dir: str | Path | None = None):
        super().__init__()
        self._model_dir = Path(model_dir) if model_dir else Path("models/whisper")
        self._session = None
        self._processor = None

    def load(self, backend: BackendType = "cpu") -> None:
        """Load Whisper model with the specified backend.

        Args:
            backend: "cpu" or "qnn_npu".
        """
        actual_backend = self._resolve_backend(backend)
        providers = self._get_ort_providers(actual_backend)

        # TODO: Load ONNX model from self._model_dir
        # For now, mark as loaded with a stub
        self._backend = actual_backend
        self._loaded = True
        print(f"ASREngine loaded with backend: {actual_backend}")

    def unload(self) -> None:
        """Release model resources."""
        self._session = None
        self._processor = None
        self._loaded = False
        self._backend = None

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> TranscriptionResult:
        """Transcribe audio to text.

        Args:
            audio: Audio waveform as numpy array (mono, float32).
            sample_rate: Sample rate of the audio (default 16000 Hz).

        Returns:
            TranscriptionResult with text, language, confidence, and latency.

        Raises:
            RuntimeError: If engine is not loaded.
        """
        if not self._loaded:
            raise RuntimeError("ASREngine not loaded. Call load() first.")

        start = time.perf_counter()

        # TODO: Implement actual Whisper inference
        # Stub response for scaffold phase
        text = "[ASR stub — Whisper model not yet loaded]"
        language = "hi"
        confidence = 0.0

        latency_ms = (time.perf_counter() - start) * 1000

        return TranscriptionResult(
            text=text,
            language=language,
            confidence=confidence,
            latency_ms=latency_ms,
        )
