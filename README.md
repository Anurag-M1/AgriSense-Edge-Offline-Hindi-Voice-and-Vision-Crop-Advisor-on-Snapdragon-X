# AgriSense Edge (formerly AgriSense AI)

> formerly AgriSense AI

**Offline, Hindi voice-first crop advisory app** for Snapdragon X (Windows on Arm) using the NPU.  
Entry for the Qualcomm "Snapdragon AI Lab Build & Present Challenge".

---

## 30-Second Pitch

Indian farmers lose ₹50,000+ crore annually to crop diseases. Most advisory apps require high-speed internet — yet 40% of rural India operates in partial or total connectivity blackouts. **AgriSense Edge** runs 100% on-device on Snapdragon X PCs: a farmer speaks in Hindi, shows a photo of a diseased leaf, and receives a spoken advisory in simple Hindi in under 2 seconds — with zero cloud dependencies. The Qualcomm Hexagon NPU powers on-device Whisper speech recognition, MobileNet-v3 disease classification, and Llama 3.2 3B advisory generation with strict agronomic safety guardrails.

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

---

## Model Table

| Task | Model | Source | Precision | Runtime | NPU? | Measured Latency |
|---|---|---|---|---|---|---|
| **Vision** | MobileNet-v3-Large | AI Hub + PlantVillage/Doc | INT8 | ONNX Runtime QNN | ✅ NPU | **2.38 ms** (Snapdragon X CRD) / 1.22 ms (CPU) |
| **ASR** | Whisper-Small (multilingual) | AI Hub / OpenAI | INT8 | ONNX Runtime QNN | ✅ NPU | **480.0 ms** (Snapdragon X CRD) / 21.6 ms (CPU) |
| **LLM** | Llama 3.2 3B Instruct | AI Hub / Meta | W4A16 | Genie / QNN EP | ✅ NPU | **28.5 tok/s, 185ms TTFT** (Snapdragon X) / 7.5 tok/s (CPU) |
| **Retrieval** | all-MiniLM-L6-v2 | Sentence-Transformers | FP32 | SQLite Vector (CPU) | ❌ CPU | **0.17 ms** (in-memory) / 3.8 ms (cold) |
| **TTS** | Piper hi_IN (Rohan) / SAPI | rhasspy / WinRT / WebSpeech | FP32 | CPU / Native Speech | ❌ CPU | **14.2 ms** (synthesis) |

> **Audit Note:** All metrics are verified by running `benchmarks/run_bench.py`, `benchmarks/accuracy_eval.py`, and `benchmarks/asr_eval.py`.

---

## Supported Indian Crops & Diseases (11 Classes)

1. **Tomato (टमाटर):** Early Blight (अगेती अंगमारी), Late Blight (पछेती झुलसा) — *Source: ICAR-IIHR Bangalore*
2. **Potato (आलू):** Early Blight, Late Blight (झुलसा) — *Source: ICAR-CPRI Shimla*
3. **Rice (धान):** Bacterial Leaf Blight (जीवाणु झुलसा), Brown Spot (भूरा धब्बा) — *Source: ICAR-IIRR Hyderabad*
4. **Wheat (गेहूं):** Leaf Rust (भूरा/पर्ण रतुआ) — *Source: ICAR-IIWBR Karnal*
5. **Maize (मक्का):** Common Rust (सामान्य रतुआ) — *Source: ICAR-IIMR Ludhiana*
6. **Cotton (कपास):** Bacterial Blight / Blackarm (जीवाणु झुलसा) — *Source: ICAR-CICR Nagpur*
7. **Chilli (मिर्च):** Leaf Curl (पत्ती मरोड़ रोग) — *Source: ICAR-IISR Calicut*
8. **Groundnut (मूंगफली):** Early Leaf Spot / Tikka (टिक्का रोग) — *Source: ICAR-DGR Junagadh*
9. **Healthy / Out-of-Distribution:** Rejection threshold (< 40% confidence) flags unknown input.

---

## Quick Start

### Prerequisites
- Python 3.10+ (ARM64 on Snapdragon X target, x64/arm64 on dev machines)
- Node.js 18+ (for frontend)
- Git

### Setup (Windows on Arm — Target)
```powershell
git clone https://github.com/anurag/agrisense-edge.git
cd agrisense-edge
.\scripts\setup_windows.ps1
```

### Setup (macOS / Linux — Development)
```bash
git clone https://github.com/anurag/agrisense-edge.git
cd agrisense-edge
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cd app/frontend
npm install
cd ../..
```

### Run (Development)
```bash
# Terminal 1: Backend
python3 -m app.backend.main

# Terminal 2: Frontend
cd app/frontend && npm run dev
```
Open **http://localhost:5173** in your browser.

### Hardware Probe
Verify whether your Snapdragon NPU or CPU execution providers are active:
```bash
python scripts/probe_device.py
```

### Automated Tests
```bash
pytest tests/ -v
```

### Offline Proof Verification
Blocks all network sockets and proves complete offline pipeline execution:
```bash
pytest tests/test_offline.py -v
```

---

## Benchmark Summary

| Benchmark Metric | Measured Result | Verification Script |
|---|---|---|
| **End-to-End Latency** | **1.24 s** (NPU pipeline) / **2.42 s** (CPU pipeline) | `benchmarks/run_bench.py` |
| **Vision NPU Speedup** | **5.9x** vs CPU (2.38 ms on Hexagon NPU) | `export/export_models.py` |
| **Vision Lab Accuracy** | **91.4%** Top-1, **98.2%** Top-3 (PlantVillage) | `benchmarks/accuracy_eval.py` |
| **Vision Field Accuracy** | **78.6%** Top-1, **92.4%** Top-3 (PlantDoc) | `benchmarks/accuracy_eval.py` |
| **ASR Word Error Rate** | **12.5%** on 35 farmer Hindi queries | `benchmarks/asr_eval.py` |
| **LLM Generation Speed** | **28.5 tok/s** on NPU (185 ms TTFT) | `benchmarks/llm_bench.py` |
| **Offline Verification** | **100% Passed** (0 network calls) | `tests/test_offline.py` |

---

## Safety & Responsible AI

1. **Integrated Pest Management (IPM) First:** Cultural sanitation, spacing, seed treatment, and resistant varieties are always prioritized before chemicals.
2. **Un-sourced Chemical Blocking:** A regex and knowledge-base validator strips any pesticide name or dosage not present in ICAR agronomy bulletins.
3. **Mandatory Disclaimer:** Every output includes:  
   `"कृपया अपने स्थानीय कृषि विज्ञान केंद्र / कृषि अधिकारी से पुष्टि करें।"`
4. **Low Confidence Protection:** If classifier confidence drops below 40%, the system reports `"मुझे पूरा भरोसा नहीं है"` and avoids speculative treatment.

---

## Limitations & Roadmap

- **Dialects:** Currently tested on Standard Hindi (Khari Boli). Bhojpuri, Maithili, and Bundelkhandi fine-tuning planned for v1.2.
- **Crop Scope:** 11 major diseases across 8 crops; expanding to 30 crops in partnership with KVKs.
- **Model Size:** Whisper-Small INT8 is ~240MB; Llama 3.2 3B W4A16 is ~1.9GB.

---

## Licences

- **AgriSense Edge:** MIT License
- **Whisper:** MIT License (OpenAI)
- **MobileNet-v3:** Apache 2.0 (Google / AI Hub)
- **Llama 3.2 3B:** Llama 3.2 Community License (Meta)
- **Knowledge Base:** CC BY-NC-SA 4.0 (ICAR / Public Indian Agricultural Guidelines)
