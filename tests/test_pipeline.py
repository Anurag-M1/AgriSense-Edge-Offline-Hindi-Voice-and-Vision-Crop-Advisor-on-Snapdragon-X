"""
test_pipeline.py — Pipeline integration tests for AgriSense Edge.
"""

import numpy as np
import pytest

from app.backend.pipeline import Pipeline, PipelineStage


class TestPipeline:
    """Test the pipeline orchestrator."""

    def test_pipeline_with_image_and_text(self, test_pipeline, sample_image):
        """Run pipeline with image and text input (bypass ASR)."""
        result = test_pipeline.run(
            image=sample_image,
            text_input="इस पत्ती में क्या बीमारी है?",
        )
        assert result.total_latency_ms >= 0
        assert len(result.stages) > 0

    def test_pipeline_with_audio_and_image(self, test_pipeline, sample_audio, sample_image):
        """Run pipeline with both audio and image."""
        result = test_pipeline.run(
            audio=sample_audio,
            image=sample_image,
        )
        assert result.total_latency_ms >= 0
        # Should have ASR + Vision + Retrieval + LLM stages at minimum
        stage_names = [s.stage for s in result.stages]
        assert PipelineStage.ASR in stage_names
        assert PipelineStage.VISION in stage_names

    def test_pipeline_stage_callback(self, test_pipeline, sample_image):
        """Verify stage callbacks are called."""
        stages_seen = []
        test_pipeline.set_stage_callback(lambda s: stages_seen.append(s))

        test_pipeline.run(image=sample_image, text_input="test")
        assert len(stages_seen) > 0
        assert PipelineStage.DONE in stages_seen

    def test_pipeline_text_only(self, test_pipeline):
        """Run pipeline with text input only (no image, no audio)."""
        result = test_pipeline.run(text_input="टमाटर में क्या बीमारी आती है?")
        assert result.total_latency_ms >= 0
