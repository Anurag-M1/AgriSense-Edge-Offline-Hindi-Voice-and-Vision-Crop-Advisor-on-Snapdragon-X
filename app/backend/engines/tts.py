"""
tts.py — Text-to-Speech engine for AgriSense Edge.

Wraps Piper TTS with Hindi voices for spoken advisory output.
Falls back to text-only if no TTS is available.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.backend.engines.base import BackendType, EngineBase


@dataclass
class SpeechResult:
    """Result of text-to-speech synthesis."""

    audio: np.ndarray | None  # PCM audio data (mono, int16)
    sample_rate: int
    latency_ms: float
    tts_available: bool
    engine_name: str  # "piper", "windows_sapi", "none"


class TTSEngine(EngineBase):
    """Piper-based Hindi text-to-speech engine."""

    def __init__(self, model_dir: str | Path | None = None, voice: str = "hi_IN-rohan-medium"):
        super().__init__()
        self._model_dir = Path(model_dir) if model_dir else Path("models/tts")
        self._voice = voice
        self._piper = None
        self._tts_available = False

    def load(self, backend: BackendType = "cpu") -> None:
        """Load TTS engine.

        TTS always runs on CPU (Piper uses ONNX Runtime CPU).
        The backend parameter is accepted for interface consistency but ignored.
        """
        self._backend = "cpu"  # TTS is always CPU

        # TODO: Try loading Piper with Hindi voice
        # Fallback chain: Piper → Windows SAPI Hindi → text-only

        self._loaded = True
        self._tts_available = False  # Will be True once Piper is integrated
        print(f"TTSEngine loaded (TTS available: {self._tts_available})")

    def unload(self) -> None:
        """Release TTS resources."""
        self._piper = None
        self._loaded = False
        self._backend = None
        self._tts_available = False

    def synthesize(self, text: str) -> SpeechResult:
        """Convert Hindi text to speech audio.

        Args:
            text: Hindi text to speak.

        Returns:
            SpeechResult with audio data, sample rate, and availability info.

        Raises:
            RuntimeError: If engine is not loaded.
        """
        if not self._loaded:
            raise RuntimeError("TTSEngine not loaded. Call load() first.")

        start = time.perf_counter()

        if not self._tts_available:
            latency_ms = (time.perf_counter() - start) * 1000
            return SpeechResult(
                audio=None,
                sample_rate=22050,
                latency_ms=latency_ms,
                tts_available=False,
                engine_name="none",
            )

        # TODO: Implement Piper synthesis
        # Stub for scaffold phase
        audio = np.zeros(22050, dtype=np.int16)  # 1 second of silence
        latency_ms = (time.perf_counter() - start) * 1000

        return SpeechResult(
            audio=audio,
            sample_rate=22050,
            latency_ms=latency_ms,
            tts_available=True,
            engine_name="piper",
        )

    @property
    def is_tts_available(self) -> bool:
        """Check if TTS synthesis is available."""
        return self._tts_available
