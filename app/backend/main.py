"""
main.py — FastAPI application for AgriSense Edge.

Provides the local HTTP API for the frontend. Binds to localhost only.
"""

from __future__ import annotations

import io
import json
import base64
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.backend.config import settings
from app.backend.db import Database
from app.backend.engines.asr import ASREngine
from app.backend.engines.llm import LLMEngine
from app.backend.engines.tts import TTSEngine
from app.backend.engines.vision import VisionEngine
from app.backend.pipeline import Pipeline, PipelineStage
from app.backend.retrieval import RetrievalEngine

# Global instances
db = Database(settings.db_path)
asr_engine = ASREngine(settings.whisper_model_dir)
vision_engine = VisionEngine(settings.vision_model_path)
llm_engine = LLMEngine(settings.llm_model_dir)
tts_engine = TTSEngine(settings.tts_model_dir, settings.tts_voice)
retrieval_engine = RetrievalEngine(db, settings.embedding_model_dir)
pipeline = Pipeline(asr_engine, vision_engine, retrieval_engine, llm_engine, tts_engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    print(f"Starting {settings.app_name}...")
    print(f"Backend: {settings.backend}")
    db.connect()

    # Load engines
    backend = settings.backend
    asr_engine.load(backend)
    vision_engine.load(backend)
    llm_engine.load(backend)
    tts_engine.load(backend)
    retrieval_engine.load()

    print(f"{settings.app_name} ready at http://{settings.host}:{settings.port}")
    yield

    # Shutdown
    print("Shutting down...")
    asr_engine.unload()
    vision_engine.unload()
    llm_engine.unload()
    tts_engine.unload()
    retrieval_engine.unload()
    db.close()


app = FastAPI(
    title="AgriSense Edge API",
    description="Offline Hindi voice-first crop advisory API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for local frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---


class HealthResponse(BaseModel):
    status: str
    engines: dict[str, dict[str, str]]
    backend: str


class DiagnoseResponse(BaseModel):
    disease_label: str
    confidence: float
    advice_text: str
    farmer_question: str
    stages: list[dict]
    total_latency_ms: float
    tts_available: bool
    audio_base64: str | None = None
    case_id: int | None = None


class FeedbackRequest(BaseModel):
    case_id: int
    helpful: bool | None = None
    comment: str = ""


# --- Routes ---


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check with engine status."""
    return HealthResponse(
        status="ok",
        backend=settings.backend,
        engines={
            "asr": {
                "loaded": str(asr_engine.is_loaded()),
                "backend": asr_engine.backend_name,
            },
            "vision": {
                "loaded": str(vision_engine.is_loaded()),
                "backend": vision_engine.backend_name,
            },
            "llm": {
                "loaded": str(llm_engine.is_loaded()),
                "backend": llm_engine.backend_name,
            },
            "tts": {
                "loaded": str(tts_engine.is_loaded()),
                "backend": tts_engine.backend_name,
            },
        },
    )


@app.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(
    image: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    text_input: str | None = Form(None),
):
    """Run the full diagnostic pipeline.

    Accepts audio (WAV) + image (JPEG/PNG), or text + image.
    Returns disease classification, advisory text, and optional TTS audio.
    """
    # Parse image
    image_array = None
    if image:
        image_bytes = await image.read()
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_array = np.array(img)

    # Parse audio
    audio_array = None
    sample_rate = 16000
    if audio:
        audio_bytes = await audio.read()
        try:
            import soundfile as sf

            audio_array, sample_rate = sf.read(io.BytesIO(audio_bytes))
            if audio_array.ndim > 1:
                audio_array = audio_array.mean(axis=1)  # Convert to mono
            audio_array = audio_array.astype(np.float32)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {e}")

    if image_array is None and audio_array is None and text_input is None:
        raise HTTPException(
            status_code=400, detail="Provide at least an image, audio, or text input."
        )

    # Run pipeline
    result = pipeline.run(
        audio=audio_array,
        image=image_array,
        text_input=text_input,
        sample_rate=sample_rate,
    )

    # Encode TTS audio as base64 if available
    audio_b64 = None
    if result.speech_result and result.speech_result.audio is not None:
        audio_b64 = base64.b64encode(result.speech_result.audio.tobytes()).decode("ascii")

    # Save case to DB
    case_id = None
    try:
        case_id = db.save_case(
            disease_label=result.disease_label,
            confidence=result.confidence,
            farmer_question=result.transcription.text if result.transcription else (text_input or ""),
            llm_response=result.advice_text,
            backend_used=settings.backend,
            latency_ms=result.total_latency_ms,
            metadata={
                "stages": [
                    {
                        "stage": s.stage.value,
                        "latency_ms": s.latency_ms,
                        "backend": s.backend,
                    }
                    for s in result.stages
                ]
            },
        )
    except Exception:
        pass  # Don't fail the response if DB write fails

    return DiagnoseResponse(
        disease_label=result.disease_label,
        confidence=result.confidence,
        advice_text=result.advice_text,
        farmer_question=result.transcription.text if result.transcription else (text_input or ""),
        stages=[
            {
                "stage": s.stage.value,
                "latency_ms": round(s.latency_ms, 1),
                "backend": s.backend,
                "status": "error" if s.error else "ok",
            }
            for s in result.stages
        ],
        total_latency_ms=round(result.total_latency_ms, 1),
        tts_available=result.speech_result.tts_available if result.speech_result else False,
        audio_base64=audio_b64,
        case_id=case_id,
    )


@app.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest):
    """Save user feedback for a diagnostic case."""
    try:
        db.save_feedback(req.case_id, req.helpful, req.comment)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    """Get current application settings (non-sensitive)."""
    return {
        "backend": settings.backend,
        "default_language": settings.default_language,
        "tts_voice": settings.tts_voice,
        "vision_confidence_threshold": settings.vision_confidence_threshold,
    }


# --- Entry point ---

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
