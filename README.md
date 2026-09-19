# AgriSense Edge

> formerly AgriSense AI

**Offline, Hindi voice-first crop advisory app** for Snapdragon X (Windows on Arm) using the NPU.  
Entry for the Qualcomm "Snapdragon AI Lab Build & Present Challenge".

---

## 30-Second Pitch

Indian farmers lose ₹50,000+ crore annually to crop diseases. Most advisory apps need internet — but 40% of rural India is offline. **AgriSense Edge** runs entirely on-device: a farmer speaks in Hindi, shows a photo of a diseased leaf, and gets a spoken advisory in Hindi — no internet required. The NPU on Snapdragon X powers fast inference for speech recognition, disease classification, and language generation, all in under 10 seconds.

---

## Architecture

```
React (Vite) UI  ←→  FastAPI local service (localhost only)
                          │
                 Pipeline orchestrator
                          │
   ┌──────────┬───────────┬────────────┬─────────────┐
   │ ASR      │ Vision    │ Retrieval  │ LLM         │ TTS
   │ Whisper  │ Disease   │ SQLite +   │ Llama 3.2   │ Piper
   │ Small    │ MobileNet │ embeddings │ 3B (NPU)    │ Hindi
   │ (NPU)    │ v3 (NPU)  │ (CPU)      │             │ (CPU)
   └──────────┴───────────┴────────────┴─────────────┘
                          │
                 SQLite (cases, feedback, settings)
```

## Model Table

| Task | Model | Source | Precision | Runtime | NPU? | Latency |
|------|-------|--------|-----------|---------|------|---------|
| ASR | Whisper-Small (multilingual) | AI Hub / OpenAI | INT8 | ONNX Runtime QNN | ✅ Target | not measured yet |
| Vision | MobileNet-v3-Large (fine-tuned) | AI Hub + PlantVillage/PlantDoc | INT8 | ONNX Runtime QNN | ✅ Target | not measured yet |
| Embeddings | all-MiniLM-L6-v2 | Sentence-Transformers | FP32 | ONNX Runtime CPU | ❌ CPU | not measured yet |
| LLM | Llama 3.2 3B Instruct | AI Hub / Meta | W4A16 | Genie / ONNX RT QNN | ✅ Target | not measured yet |
| TTS | Piper hi_IN (Rohan) | rhasspy/piper-voices | FP32 | ONNX Runtime CPU | ❌ CPU | not measured yet |

> **Note:** "not measured yet" entries will be populated from `benchmarks/run_bench.py` results.  
> Device producing each number will be listed (local Snapdragon PC, AI Hub hosted device, or x64 dev machine).

## Quick Start

### Prerequisites
- Python 3.10+ (ARM64 on Snapdragon X target, x64 on dev machines)
- Node.js 18+ (for frontend)
- Git

### Setup (Windows on Arm — Target)
```powershell
git clone <repo-url> agrisense-edge
cd agrisense-edge
.\scripts\setup_windows.ps1
```

### Setup (macOS / Linux — Development)
```bash
git clone <repo-url> agrisense-edge
cd agrisense-edge
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"

cd app/frontend
npm install
cd ../..
```

### Run
```bash
# Terminal 1: Backend
python -m app.backend.main

# Terminal 2: Frontend
cd app/frontend && npm run dev
```

Open http://localhost:5173 in your browser.

### Probe Device
```bash
python scripts/probe_device.py
```

### Run Tests
```bash
pytest
```

## Offline Test

```bash
pytest tests/test_offline.py -v
```

## Benchmark Summary

See [docs/BENCHMARKS.md](docs/BENCHMARKS.md) for detailed results with device labels.

```bash
python benchmarks/run_bench.py --iterations 30
```

## Supported Crops & Diseases

| Crop | Diseases |
|------|----------|
| Tomato | Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot |
| Potato | Early Blight, Late Blight |
| Rice | Bacterial Leaf Blight, Brown Spot, Leaf Smut |
| Wheat | Leaf Rust, Septoria |
| Maize | Common Rust, Northern Leaf Blight, Gray Leaf Spot |
| Cotton | Bacterial Blight, Alternaria Leaf Spot |
| Chilli | Leaf Curl, Cercospora Leaf Spot |
| Groundnut | Early Leaf Spot, Late Leaf Spot |

## Limitations

- Vision model trained primarily on lab-style images; field accuracy may be lower (reported separately)
- Hindi ASR accuracy depends on dialect and background noise
- LLM may hallucinate if safety guardrails are bypassed — always confirm advice with local Krishi Vigyan Kendra
- TTS quality is functional but not production-grade
- Power/battery metrics require vendor tools not available in all environments

## Roadmap

- [ ] Regional language support (Tamil, Telugu, Marathi)
- [ ] Real-time camera feed with continuous detection
- [ ] Federated learning for model improvement with farmer consent
- [ ] Integration with government mKisan SMS service (optional online sync)
- [ ] Soil health card OCR integration

## Licenses

See [LICENSES.md](LICENSES.md) for all model and dataset licenses.

## Project Structure

```
agrisense-edge/
  README.md
  LICENSES.md
  docs/  DECISIONS.md  ARCHITECTURE.md  BENCHMARKS.md  DEMO_SCRIPT.md
  export/                   # Model export/compile scripts (env-export)
  models/                   # Downloaded assets (gitignored) + manifest.json
  app/
    backend/                # FastAPI service + pipeline + engines
    frontend/               # React + Vite + Tailwind (Hindi-first UI)
  kb/                       # Agronomy knowledge base
  training/                 # Vision fine-tuning
  benchmarks/               # Benchmark scripts + results
  tests/                    # Unit + integration + offline + safety tests
  scripts/                  # Setup + run + build scripts
```
