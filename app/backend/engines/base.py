"""
base.py — Abstract base class for all AgriSense Edge inference engines.

Each engine wraps a model with at least two backends:
  - cpu: ONNX Runtime CPUExecutionProvider (works everywhere)
  - qnn_npu: ONNX Runtime QNNExecutionProvider (Snapdragon X only)

A config flag selects the backend so benchmarks can compare NPU vs CPU
on the same code path.
"""

from abc import ABC, abstractmethod
from typing import Literal

BackendType = Literal["cpu", "qnn_npu"]


class EngineBase(ABC):
    """Abstract base for all inference engines."""

    def __init__(self):
        self._backend: BackendType | None = None
        self._loaded: bool = False

    @abstractmethod
    def load(self, backend: BackendType = "cpu") -> None:
        """Load the model with the specified backend.

        Args:
            backend: "cpu" for CPUExecutionProvider, "qnn_npu" for QNNExecutionProvider.
        """
        ...

    @abstractmethod
    def unload(self) -> None:
        """Release model resources."""
        ...

    def is_loaded(self) -> bool:
        """Check if the model is currently loaded."""
        return self._loaded

    @property
    def backend_name(self) -> str:
        """Return the name of the currently active backend."""
        return self._backend or "none"

    def _get_ort_providers(self, backend: BackendType) -> list[str]:
        """Get ONNX Runtime execution providers for the given backend.

        Args:
            backend: The target backend.

        Returns:
            List of execution provider names.
        """
        if backend == "qnn_npu":
            return ["QNNExecutionProvider", "CPUExecutionProvider"]
        return ["CPUExecutionProvider"]

    def _resolve_backend(self, backend: BackendType) -> BackendType:
        """Resolve backend, falling back to CPU if QNN is not available.

        Args:
            backend: Requested backend.

        Returns:
            The actual backend that will be used.
        """
        if backend == "qnn_npu":
            try:
                import onnxruntime as ort

                available = ort.get_available_providers()
                if "QNNExecutionProvider" not in available:
                    # Try plugin registration
                    try:
                        import onnxruntime_qnn as qnn_ep

                        ort.register_execution_provider_library(
                            "QNNExecutionProvider", qnn_ep.get_library_path()
                        )
                        available = ort.get_available_providers()
                    except (ImportError, Exception):
                        pass

                if "QNNExecutionProvider" not in available:
                    print(
                        f"⚠️  QNN EP not available, falling back to CPU for {self.__class__.__name__}"
                    )
                    return "cpu"
            except ImportError:
                print(
                    f"⚠️  onnxruntime not installed, falling back to CPU for {self.__class__.__name__}"
                )
                return "cpu"
        return backend
