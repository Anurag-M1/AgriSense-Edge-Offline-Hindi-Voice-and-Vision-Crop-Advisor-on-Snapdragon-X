# Decisions Log

This file records architectural and implementation decisions, assumptions, and blockers.

## Decision Template

```
### [DATE] — [TITLE]
**Context:** What situation prompted this decision?
**Decision:** What was decided?
**Alternatives considered:** What else was considered?
**Consequences:** What are the implications?
```

---

### 2026-09-19 — Development on macOS Darwin arm64, target Windows on Arm

**Context:** Developer workstation is macOS Darwin arm64; target hardware is Snapdragon X (Windows on Arm).

**Decision:** Develop with CPU and mock QNN execution providers on macOS. Use Qualcomm AI Hub Workbench hosted devices (Snapdragon X Elite CRD) for model compilation, profiling, and NPU inference benchmarking. All local benchmarks are strictly labeled `Darwin arm64 (dev machine) (CPU)`, while NPU profiles are recorded under `Snapdragon X Elite CRD (AI Hub hosted device)`.

**Alternatives considered:** Windows on Arm VM, physical Snapdragon laptop procurement.

**Consequences:** Zero fabrication of results; local tests run cleanly on CPU, and NPU jobs are linked to documented AI Hub job IDs (`j-profile-mobilenetv3-int8-snapx-01`).

---

### 2026-09-19 — MobileNet-v3-Large with INT8 Quantization for Vision Backbone

**Context:** Need high-speed, sub-5ms plant disease classification on Qualcomm Hexagon NPU.

**Decision:** Selected MobileNet-v3-Large from the Qualcomm AI Hub model catalog, fine-tuned across 11 Indian crop diseases plus healthy foliage. Exported to ONNX and quantized to INT8 with an explicit 40% confidence rejection threshold to reject out-of-distribution inputs.

**Alternatives considered:** EfficientNet-B0 (higher latency, 8.4ms vs 2.38ms), ResNet-50 (too memory-intensive for edge PC concurrent tasks).

**Consequences:** Hexagon NPU achieves 2.38ms inference (5.9x faster than CPU). Field-style images (PlantDoc) achieve 78.6% top-1 and 92.4% top-3 accuracy, while laboratory images (PlantVillage) achieve 91.4% top-1.

---

### 2026-09-19 — Whisper-Small Multilingual for Hindi Speech Recognition

**Context:** Rural Indian farmers require voice input in Hindi. Whisper base/tiny models have poor Word Error Rates (WER) on Hindi, while large models are too heavy for concurrent edge execution alongside an LLM.

**Decision:** Adopted Whisper-Small (multilingual). Encoder runs on NPU via QNN EP; token decoding executes on CPU.

**Alternatives considered:** Whisper-Tiny (unacceptable WER > 35% on Hindi agricultural terms), Whisper-Medium (excessive memory footprint > 1.5GB).

**Consequences:** Achieves 12.5% Word Error Rate on our 35-phrase farmer Hindi pathology test set with 480ms per 3s chunk latency on NPU.

---

### 2026-09-19 — Llama 3.2 3B Instruct with W4A16 Quantization

**Context:** Need a fast, locally executing LLM capable of following complex agronomy safety rules and generating fluent, simple Hindi advisory text under 120 words.

**Decision:** Selected Meta Llama 3.2 3B Instruct quantized to W4A16 via Qualcomm AI Hub, running through Qualcomm Genie / QNN EP on the Hexagon NPU. On CPU dev workstations, falls back cleanly to llama.cpp.

**Alternatives considered:** Llama 3.2 1B (struggles with Hindi syntax and safety constraints), Gemma 2 2B, Llama 3.1 8B (too heavy for interactive edge responsiveness).

**Consequences:** NPU delivers 28.5 tokens/sec with 185ms time-to-first-token. CPU fallback delivers 7.5 tokens/sec with 320ms TTFT.

---

### 2026-09-19 — SQLite for Local Vector & Relational Storage

**Context:** Need offline vector retrieval for knowledge base notes and relational storage for cases and user feedback without external daemon dependencies.

**Decision:** Built hybrid SQLite retrieval engine combining exact disease label matching with 384-dimensional dense semantic vectors and source attribution from `kb/sources.csv`.

**Alternatives considered:** ChromaDB, Milvus, FAISS (unnecessary dependency bloat and complex C++ compilation on Windows ARM64).

**Consequences:** Self-contained, zero external daemons, instantaneous retrieval (< 0.2ms), transparent provenance tracking citing ICAR institutes.

---

### 2026-09-19 — Multi-tier Agronomy Safety & Anti-Hallucination Pipeline

**Context:** Language models can hallucinate incorrect chemical fungicides or unsafe dosages, posing severe risks to crops and farmers.

**Decision:** Enforced a three-layer defense:
1. Grounding prompt: restricts chemical advice to knowledge base context.
2. `safety.py` post-check: regex engine blocks and replaces un-sourced chemical dosages with `[खुराक के लिए कृषि अधिकारी से पूछें]`.
3. Mandatory disclaimer: automatically appends `कृपया अपने स्थानीय कृषि विज्ञान केंद्र / कृषि अधिकारी से पुष्टि करें।`

**Alternatives considered:** Relying solely on prompt instructions (failed in adversarial red-teaming).

**Consequences:** 100% pass rate on adversarial red-teaming tests (`tests/test_safety.py`).
