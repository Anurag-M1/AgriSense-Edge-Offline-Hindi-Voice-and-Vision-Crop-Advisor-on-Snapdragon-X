"""
llm.py — Large Language Model engine for AgriSense Edge.

Wraps Llama 3.2 3B Instruct for generating Hindi crop advisory responses.
Supports NPU via Genie/ONNX Runtime QNN, and CPU fallback via llama.cpp.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from app.backend.engines.base import BackendType, EngineBase


@dataclass
class GenerationResult:
    """Result of LLM text generation."""

    text: str
    tokens_generated: int
    tokens_per_sec: float
    time_to_first_token_ms: float
    total_latency_ms: float
    backend_used: str


# System prompt for agronomy safety
SYSTEM_PROMPT = """You are AgriSense, a Hindi-speaking crop advisory assistant for Indian farmers.

STRICT RULES:
1. Answer ONLY in simple Hindi (Devanagari script). Use short sentences.
2. Keep responses under 120 words.
3. Structure your answer as:
   - क्या दिख रहा है (What it looks like)
   - अभी क्या करें (What to do now — prefer IPM/cultural controls first)
   - विशेषज्ञ से कब पूछें (When to ask an expert)
4. NEVER invent pesticide or chemical names. Only mention chemicals that appear in the provided knowledge base notes.
5. For any chemical mention, cite the source from the knowledge base.
6. ALWAYS end with: "कृपया अपने स्थानीय कृषि विज्ञान केंद्र / कृषि अधिकारी से पुष्टि करें।"
7. If disease confidence is LOW, say "मुझे पूरा भरोसा नहीं है" and recommend expert consultation.
8. If you don't know, say "मुझे इसकी जानकारी नहीं है" — never guess.
9. Prefer integrated pest management (IPM) steps before chemical solutions.
"""


class LLMEngine(EngineBase):
    """Llama 3.2 3B based text generation engine."""

    def __init__(self, model_path: str | Path | None = None):
        super().__init__()
        self._model_path = Path(model_path) if model_path else Path("models/llm")
        self._model = None

    def load(self, backend: BackendType = "cpu") -> None:
        """Load LLM with the specified backend.

        For qnn_npu: Uses Genie or ONNX Runtime QNN EP.
        For cpu: Uses llama.cpp via llama-cpp-python.
        """
        actual_backend = self._resolve_backend(backend)

        # TODO: Load model based on backend
        # qnn_npu → Genie SDK or ONNX Runtime GenAI
        # cpu → llama-cpp-python with GGUF model

        self._backend = actual_backend
        self._loaded = True
        print(f"LLMEngine loaded with backend: {actual_backend}")

    def unload(self) -> None:
        """Release model resources."""
        self._model = None
        self._loaded = False
        self._backend = None

    def generate(
        self,
        disease_label: str,
        confidence: float,
        farmer_question: str,
        retrieved_notes: list[str],
        max_tokens: int = 300,
    ) -> GenerationResult:
        """Generate a Hindi crop advisory response.

        Args:
            disease_label: Classified disease name.
            confidence: Classification confidence (0-1).
            farmer_question: Transcribed farmer question in Hindi.
            retrieved_notes: Knowledge base entries for context.
            max_tokens: Maximum tokens to generate.

        Returns:
            GenerationResult with text, performance metrics, and backend info.

        Raises:
            RuntimeError: If engine is not loaded.
        """
        if not self._loaded:
            raise RuntimeError("LLMEngine not loaded. Call load() first.")

        start = time.perf_counter()

        # Build the prompt
        prompt = self._build_prompt(disease_label, confidence, farmer_question, retrieved_notes)

        # TODO: Implement actual generation
        # Stub response for scaffold phase
        text = "[LLM stub — model not yet loaded]"
        tokens_generated = 0
        time_to_first_token_ms = 0.0

        total_latency_ms = (time.perf_counter() - start) * 1000
        tokens_per_sec = (
            tokens_generated / (total_latency_ms / 1000) if total_latency_ms > 0 else 0
        )

        return GenerationResult(
            text=text,
            tokens_generated=tokens_generated,
            tokens_per_sec=tokens_per_sec,
            time_to_first_token_ms=time_to_first_token_ms,
            total_latency_ms=total_latency_ms,
            backend_used=self._backend or "none",
        )

    def _build_prompt(
        self,
        disease_label: str,
        confidence: float,
        farmer_question: str,
        retrieved_notes: list[str],
    ) -> str:
        """Build the full prompt with system rules, context, and question.

        Args:
            disease_label: Classified disease.
            confidence: Classification confidence.
            farmer_question: The farmer's question.
            retrieved_notes: Knowledge base entries.

        Returns:
            Formatted prompt string.
        """
        confidence_text = (
            "HIGH" if confidence >= 0.7 else "MEDIUM" if confidence >= 0.4 else "LOW"
        )

        notes_text = "\n\n".join(retrieved_notes) if retrieved_notes else "No relevant notes found."

        user_prompt = f"""Disease detected: {disease_label} (confidence: {confidence_text}, {confidence:.1%})

Knowledge base notes:
{notes_text}

Farmer's question: {farmer_question}

Provide advice following the rules in your system prompt."""

        return f"<|system|>\n{SYSTEM_PROMPT}\n<|user|>\n{user_prompt}\n<|assistant|>\n"
