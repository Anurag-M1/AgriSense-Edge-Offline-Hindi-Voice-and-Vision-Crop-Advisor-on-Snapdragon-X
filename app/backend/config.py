"""
config.py — Application configuration for AgriSense Edge.

Uses pydantic-settings for type-safe configuration from environment variables.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, configurable via environment variables."""

    # General
    app_name: str = "AgriSense Edge"
    debug: bool = False

    # Backend selection: "cpu" or "qnn_npu"
    backend: Literal["cpu", "qnn_npu"] = "cpu"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Model paths
    model_dir: Path = Path("models")
    whisper_model_dir: Path = Path("models/whisper")
    vision_model_path: Path = Path("models/vision/model.onnx")
    llm_model_dir: Path = Path("models/llm")
    tts_model_dir: Path = Path("models/tts")
    embedding_model_dir: Path = Path("models/embeddings")

    # Vision
    vision_confidence_threshold: float = 0.4

    # LLM
    llm_max_tokens: int = 300

    # TTS
    tts_voice: str = "hi_IN-rohan-medium"

    # Retrieval
    retrieval_top_k: int = 3

    # Database
    db_path: Path = Path("data/agrisense.db")

    # Knowledge base
    kb_dir: Path = Path("kb")

    # Language
    default_language: str = "hi"

    model_config = {
        "env_prefix": "AGRISENSE_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Global settings instance
settings = Settings()
