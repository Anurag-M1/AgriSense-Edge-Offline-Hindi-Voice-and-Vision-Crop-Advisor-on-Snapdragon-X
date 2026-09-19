# Architecture

## Overview

AgriSense Edge is an offline, Hindi voice-first crop advisory system. It runs as a local web application with a React frontend communicating with a FastAPI backend over localhost. All AI inference runs on-device — no internet required.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React (Vite) UI                       │
│  ┌──────┐  ┌────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Mic  │  │ Camera │  │ Progress │  │ Result Card  │  │
│  │Button│  │/Upload │  │  Ticks   │  │  + Speaker   │  │
│  └──┬───┘  └───┬────┘  └────▲─────┘  └──────▲───────┘  │
│     │          │            │               │           │
│     └──────────┴────────────┴───────────────┘           │
│                      │ HTTP/SSE                         │
└──────────────────────┼──────────────────────────────────┘
                       │ localhost:8000
┌──────────────────────┼──────────────────────────────────┐
│                FastAPI Service                          │
│                                                         │
│  POST /api/diagnose  (audio + image → streaming result) │
│  GET  /api/health                                       │
│  POST /api/feedback                                     │
│  GET  /api/settings                                     │
│                                                         │
│  ┌─────────────────────────────────────────────┐        │
│  │         Pipeline Orchestrator               │        │
│  │    (state machine: idle → asr → vision      │        │
│  │     → retrieval → llm → tts → done)         │        │
│  └────────────────┬────────────────────────────┘        │
│                   │                                     │
│  ┌────────┐ ┌─────┴────┐ ┌──────────┐ ┌─────┐ ┌─────┐ │
│  │  ASR   │ │  Vision  │ │Retrieval │ │ LLM │ │ TTS │ │
│  │Engine  │ │  Engine  │ │  Engine  │ │Eng. │ │Eng. │ │
│  └───┬────┘ └────┬─────┘ └────┬─────┘ └──┬──┘ └──┬──┘ │
│      │           │            │           │       │     │
│  ┌───┴───┐  ┌────┴────┐  ┌───┴────┐  ┌───┴──┐ ┌──┴──┐ │
│  │cpu│npu│  │cpu │npu │  │sqlite+ │  │cpu│  │ │cpu│  │ │
│  │   │   │  │    │    │  │embeddings│ │npu│  │ │   │  │ │
│  └───┴───┘  └────┴────┘  └────────┘  └───┴──┘ └──┴──┘ │
│                                                         │
│  ┌──────────────────────────────────────────────┐       │
│  │           SQLite Database                    │       │
│  │  cases │ feedback │ settings │ kb_vectors    │       │
│  └──────────────────────────────────────────────┘       │
│                                                         │
│  ┌──────────────────────────────────────────────┐       │
│  │           Safety Module                      │       │
│  │  - Block un-sourced chemical names/doses     │       │
│  │  - Force disclaimer line                     │       │
│  │  - Low-confidence downgrade                  │       │
│  └──────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Engine Interface Pattern

Each model is wrapped behind an abstract interface with at least two backends:

```python
class EngineBase(ABC):
    @abstractmethod
    def load(self, backend: Literal["cpu", "qnn_npu"]) -> None: ...

    @abstractmethod
    def is_loaded(self) -> bool: ...

    @property
    @abstractmethod
    def backend_name(self) -> str: ...
```

A configuration flag (`AGRISENSE_BACKEND`) selects the backend at startup:
- `cpu`: Uses ONNX Runtime CPUExecutionProvider (works everywhere)
- `qnn_npu`: Uses ONNX Runtime QNNExecutionProvider (Snapdragon X only)

This enables direct NPU vs CPU comparison on the same code path.

## Data Flow

1. **User Input**: Hindi speech (WAV via mic) + crop photo (JPEG via camera/upload)
2. **ASR**: Whisper-Small transcribes speech → Hindi text
3. **Vision**: MobileNet-v3 classifies image → disease label + confidence
4. **Retrieval**: Disease label → top-k knowledge base entries (pre-embedded in SQLite)
5. **LLM**: Llama 3.2 3B generates advisory using: system prompt + safety rules + KB notes + disease label + farmer question
6. **Safety Post-check**: Verify no un-sourced chemicals, force disclaimer, handle low confidence
7. **TTS**: Piper speaks the response in Hindi
8. **Output**: Result card with disease name, confidence bar, advice text, speaker button

## Directory Map

```
app/
  backend/
    main.py          # FastAPI app, CORS, startup
    pipeline.py      # Orchestrator state machine
    config.py        # Pydantic settings (backend selection, model paths)
    db.py            # SQLite connection, schema, CRUD
    retrieval.py     # Embedding + vector search
    safety.py        # LLM output post-processing
    engines/
      __init__.py
      base.py        # Abstract EngineBase
      asr.py         # ASREngine (Whisper)
      vision.py      # VisionEngine (MobileNet-v3)
      llm.py         # LLMEngine (Llama 3.2 3B)
      tts.py         # TTSEngine (Piper)
  frontend/
    src/
      App.jsx        # Main app component
      components/    # UI components
      hooks/         # Custom React hooks
      i18n/          # Hindi/English translations
```
