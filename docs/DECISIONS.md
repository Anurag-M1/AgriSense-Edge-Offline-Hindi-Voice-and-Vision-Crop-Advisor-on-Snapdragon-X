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

### 2025-XX-XX — Development on macOS, target Windows on Arm

**Context:** Developer machine is macOS; target is Snapdragon X (Windows on Arm).

**Decision:** Develop with CPU execution providers on macOS. Use Qualcomm AI Hub Workbench hosted devices (Snapdragon X Elite CRD) for model compilation, profiling, and NPU inference jobs. Maintain two documented environments: `env-export` (x64 Python for AI Hub tooling) and `env-runtime` (app execution).

**Alternatives considered:** Setting up Windows VM, buying Snapdragon hardware.

**Consequences:** All local benchmarks labeled "x64 dev machine (CPU)". NPU numbers labeled "AI Hub hosted device". Final validation must happen on actual Snapdragon X hardware.

---

### 2025-XX-XX — MobileNet-v3-Large for vision backbone

**Context:** Need a fast, accurate plant disease classifier that runs on NPU.

**Decision:** MobileNet-v3-Large with transfer learning. Available on AI Hub, good accuracy/latency tradeoff, well-supported ONNX export path.

**Alternatives considered:** EfficientNet-B0 (slightly higher accuracy but larger), ResNet-18 (too large for edge), custom CNN (too much training data needed).

**Consequences:** May need to revisit if accuracy on field-style images is below 70%.

---

### 2025-XX-XX — SQLite for vector storage instead of dedicated vector DB

**Context:** Need offline vector retrieval for knowledge base.

**Decision:** Use SQLite with numpy-based cosine similarity. Vectors stored as BLOBs.

**Alternatives considered:** ChromaDB (adds dependency, overkill for ~50 entries), FAISS (complex build for ARM64).

**Consequences:** Simple, zero-dependency, but won't scale beyond ~1000 entries efficiently. Fine for our 50-entry knowledge base.
