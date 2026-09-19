"""
vision.py — Plant disease classification engine for AgriSense Edge.

Wraps MobileNet-v3-Large (fine-tuned on PlantVillage/PlantDoc) for
crop disease detection. Supports cpu and qnn_npu backends.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.backend.engines.base import BackendType, EngineBase


@dataclass
class ClassificationResult:
    """Result of plant disease classification."""

    label: str
    confidence: float
    top_3: list[tuple[str, float]]
    is_low_confidence: bool
    latency_ms: float


# Default class labels — will be populated by training
DEFAULT_LABELS = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Rice___Bacterial_leaf_blight",
    "Rice___Brown_spot",
    "Rice___Leaf_smut",
    "Rice___healthy",
    "Wheat___Leaf_rust",
    "Wheat___Septoria",
    "Wheat___healthy",
    "Maize___Common_rust",
    "Maize___Northern_Leaf_Blight",
    "Maize___Gray_leaf_spot",
    "Maize___healthy",
    "Cotton___Bacterial_blight",
    "Cotton___Alternaria_leaf_spot",
    "Cotton___healthy",
    "Chilli___Leaf_curl",
    "Chilli___Cercospora_leaf_spot",
    "Chilli___healthy",
    "Groundnut___Early_leaf_spot",
    "Groundnut___Late_leaf_spot",
    "Groundnut___healthy",
]

# Confidence threshold for "low confidence / unknown" rejection
LOW_CONFIDENCE_THRESHOLD = 0.4


class VisionEngine(EngineBase):
    """MobileNet-v3 based plant disease classifier."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        labels: list[str] | None = None,
        confidence_threshold: float = LOW_CONFIDENCE_THRESHOLD,
    ):
        super().__init__()
        self._model_path = Path(model_path) if model_path else Path("models/vision/model.onnx")
        self._labels = labels or DEFAULT_LABELS
        self._confidence_threshold = confidence_threshold
        self._session = None

    def load(self, backend: BackendType = "cpu") -> None:
        """Load vision model with the specified backend."""
        actual_backend = self._resolve_backend(backend)
        providers = self._get_ort_providers(actual_backend)

        # TODO: Load ONNX model
        self._backend = actual_backend
        self._loaded = True
        print(f"VisionEngine loaded with backend: {actual_backend}")

    def unload(self) -> None:
        """Release model resources."""
        self._session = None
        self._loaded = False
        self._backend = None

    def classify(self, image: np.ndarray) -> ClassificationResult:
        """Classify a crop/leaf image for disease.

        Args:
            image: Image as numpy array (H, W, C) in RGB, uint8.

        Returns:
            ClassificationResult with label, confidence, top-3, and latency.

        Raises:
            RuntimeError: If engine is not loaded.
        """
        if not self._loaded:
            raise RuntimeError("VisionEngine not loaded. Call load() first.")

        start = time.perf_counter()

        # TODO: Implement actual inference
        # Stub response for scaffold phase
        label = "unknown"
        confidence = 0.0
        top_3 = [("unknown", 0.0)]
        is_low_confidence = True

        latency_ms = (time.perf_counter() - start) * 1000

        return ClassificationResult(
            label=label,
            confidence=confidence,
            top_3=top_3,
            is_low_confidence=is_low_confidence,
            latency_ms=latency_ms,
        )

    @property
    def labels(self) -> list[str]:
        """Return the list of class labels."""
        return self._labels

    @property
    def confidence_threshold(self) -> float:
        """Return the low-confidence rejection threshold."""
        return self._confidence_threshold
