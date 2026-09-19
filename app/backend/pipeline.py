"""
pipeline.py — Pipeline orchestrator for AgriSense Edge.

State machine that coordinates ASR → Vision → Retrieval → LLM → TTS
stages for a complete crop advisory interaction.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

import numpy as np

from app.backend.config import settings
from app.backend.engines.asr import ASREngine, TranscriptionResult
from app.backend.engines.llm import LLMEngine, GenerationResult
from app.backend.engines.tts import TTSEngine, SpeechResult
from app.backend.engines.vision import ClassificationResult, VisionEngine
from app.backend.retrieval import RetrievalEngine, RetrievalResult
from app.backend.safety import SafetyCheckResult, check_and_fix_response


class PipelineStage(str, Enum):
    """Pipeline execution stages."""

    IDLE = "idle"
    ASR = "asr"
    VISION = "vision"
    RETRIEVAL = "retrieval"
    LLM = "llm"
    SAFETY = "safety"
    TTS = "tts"
    DONE = "done"
    ERROR = "error"


@dataclass
class StageResult:
    """Result from a single pipeline stage."""

    stage: PipelineStage
    latency_ms: float
    backend: str
    data: Any = None
    error: str | None = None


@dataclass
class PipelineResult:
    """Complete result from the diagnostic pipeline."""

    stages: list[StageResult] = field(default_factory=list)
    total_latency_ms: float = 0.0

    # Individual results
    transcription: TranscriptionResult | None = None
    classification: ClassificationResult | None = None
    retrieved_notes: list[RetrievalResult] = field(default_factory=list)
    llm_result: GenerationResult | None = None
    safety_result: SafetyCheckResult | None = None
    speech_result: SpeechResult | None = None

    # Final output
    advice_text: str = ""
    disease_label: str = ""
    confidence: float = 0.0

    @property
    def is_success(self) -> bool:
        return all(s.error is None for s in self.stages)


class Pipeline:
    """Diagnostic pipeline orchestrator."""

    def __init__(
        self,
        asr: ASREngine,
        vision: VisionEngine,
        retrieval: RetrievalEngine,
        llm: LLMEngine,
        tts: TTSEngine,
    ):
        self._asr = asr
        self._vision = vision
        self._retrieval = retrieval
        self._llm = llm
        self._tts = tts
        self._stage_callback: Callable[[PipelineStage], None] | None = None

    def set_stage_callback(self, callback: Callable[[PipelineStage], None]) -> None:
        """Set a callback to be called when the pipeline enters a new stage."""
        self._stage_callback = callback

    def _notify_stage(self, stage: PipelineStage) -> None:
        if self._stage_callback:
            self._stage_callback(stage)

    def run(
        self,
        audio: np.ndarray | None = None,
        image: np.ndarray | None = None,
        text_input: str | None = None,
        sample_rate: int = 16000,
    ) -> PipelineResult:
        """Run the full diagnostic pipeline.

        Args:
            audio: Audio waveform (mono, float32) for ASR. Optional if text_input provided.
            image: Crop/leaf image (H, W, C, uint8 RGB) for vision classification.
            text_input: Direct text input (bypasses ASR). Used if audio is None.
            sample_rate: Audio sample rate (default 16000).

        Returns:
            PipelineResult with all stage results.
        """
        result = PipelineResult()
        pipeline_start = time.perf_counter()

        # Stage 1: ASR
        farmer_question = text_input or ""
        if audio is not None:
            self._notify_stage(PipelineStage.ASR)
            try:
                stage_start = time.perf_counter()
                transcription = self._asr.transcribe(audio, sample_rate)
                result.transcription = transcription
                farmer_question = transcription.text
                result.stages.append(
                    StageResult(
                        stage=PipelineStage.ASR,
                        latency_ms=transcription.latency_ms,
                        backend=self._asr.backend_name,
                        data={"text": transcription.text, "language": transcription.language},
                    )
                )
            except Exception as e:
                result.stages.append(
                    StageResult(
                        stage=PipelineStage.ASR,
                        latency_ms=(time.perf_counter() - stage_start) * 1000,
                        backend=self._asr.backend_name,
                        error=str(e),
                    )
                )

        # Stage 2: Vision
        if image is not None:
            self._notify_stage(PipelineStage.VISION)
            try:
                stage_start = time.perf_counter()
                classification = self._vision.classify(image)
                result.classification = classification
                result.disease_label = classification.label
                result.confidence = classification.confidence
                result.stages.append(
                    StageResult(
                        stage=PipelineStage.VISION,
                        latency_ms=classification.latency_ms,
                        backend=self._vision.backend_name,
                        data={
                            "label": classification.label,
                            "confidence": classification.confidence,
                            "top_3": classification.top_3,
                        },
                    )
                )
            except Exception as e:
                result.stages.append(
                    StageResult(
                        stage=PipelineStage.VISION,
                        latency_ms=(time.perf_counter() - stage_start) * 1000,
                        backend=self._vision.backend_name,
                        error=str(e),
                    )
                )

        # Stage 3: Retrieval
        self._notify_stage(PipelineStage.RETRIEVAL)
        try:
            stage_start = time.perf_counter()
            retrieved = self._retrieval.retrieve(
                disease_label=result.disease_label,
                question=farmer_question,
                top_k=settings.retrieval_top_k,
            )
            result.retrieved_notes = retrieved
            retrieval_latency = (time.perf_counter() - stage_start) * 1000
            result.stages.append(
                StageResult(
                    stage=PipelineStage.RETRIEVAL,
                    latency_ms=retrieval_latency,
                    backend="cpu",
                    data={"num_results": len(retrieved)},
                )
            )
        except Exception as e:
            result.stages.append(
                StageResult(
                    stage=PipelineStage.RETRIEVAL,
                    latency_ms=(time.perf_counter() - stage_start) * 1000,
                    backend="cpu",
                    error=str(e),
                )
            )

        # Stage 4: LLM
        self._notify_stage(PipelineStage.LLM)
        try:
            stage_start = time.perf_counter()
            note_texts = [r.text for r in result.retrieved_notes]
            llm_result = self._llm.generate(
                disease_label=result.disease_label,
                confidence=result.confidence,
                farmer_question=farmer_question,
                retrieved_notes=note_texts,
                max_tokens=settings.llm_max_tokens,
            )
            result.llm_result = llm_result
            result.stages.append(
                StageResult(
                    stage=PipelineStage.LLM,
                    latency_ms=llm_result.total_latency_ms,
                    backend=llm_result.backend_used,
                    data={
                        "tokens_generated": llm_result.tokens_generated,
                        "tokens_per_sec": llm_result.tokens_per_sec,
                    },
                )
            )

            # Stage 4b: Safety post-processing
            self._notify_stage(PipelineStage.SAFETY)
            safety_result = check_and_fix_response(
                llm_text=llm_result.text,
                retrieved_notes=note_texts,
                disease_confidence=result.confidence,
                confidence_threshold=settings.vision_confidence_threshold,
            )
            result.safety_result = safety_result
            result.advice_text = safety_result.processed_text

        except Exception as e:
            result.stages.append(
                StageResult(
                    stage=PipelineStage.LLM,
                    latency_ms=(time.perf_counter() - stage_start) * 1000,
                    backend=self._llm.backend_name,
                    error=str(e),
                )
            )

        # Stage 5: TTS
        if result.advice_text:
            self._notify_stage(PipelineStage.TTS)
            try:
                stage_start = time.perf_counter()
                speech = self._tts.synthesize(result.advice_text)
                result.speech_result = speech
                result.stages.append(
                    StageResult(
                        stage=PipelineStage.TTS,
                        latency_ms=speech.latency_ms,
                        backend="cpu",
                        data={"tts_available": speech.tts_available},
                    )
                )
            except Exception as e:
                result.stages.append(
                    StageResult(
                        stage=PipelineStage.TTS,
                        latency_ms=(time.perf_counter() - stage_start) * 1000,
                        backend="cpu",
                        error=str(e),
                    )
                )

        # Finalize
        self._notify_stage(PipelineStage.DONE)
        result.total_latency_ms = (time.perf_counter() - pipeline_start) * 1000

        return result
