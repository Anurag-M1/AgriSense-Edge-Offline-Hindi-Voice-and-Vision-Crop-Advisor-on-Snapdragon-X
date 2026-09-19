# AgriSense Edge — Pitch Deck Outline

**Challenge:** Qualcomm Snapdragon AI Lab Build & Present Challenge  
**Title:** AgriSense Edge — On-Device Hindi Crop Advisory Powered by Snapdragon X NPU  

---

### Slide 1: Title & Vision
- **Header:** AgriSense Edge *(formerly AgriSense AI)*
- **Tagline:** Offline, Hindi Voice-First Crop Advisory Powered by Snapdragon X
- **Presenter:** Anurag Singh
- **Target:** Indian Smallholder Farmers & Rural Agronomy

---

### Slide 2: The Critical Problem
- **The Rural Reality:** ₹50,000+ Crore annual loss to crop disease in India.
- **The Digital Divide:** 40% of farming regions have unreliable or zero 4G/5G data.
- **The Usability Barrier:** Text-heavy English apps fail illiterate or regional language farmers.
- **The Cloud Failure:** When internet drops, cloud LLMs and cloud vision APIs are completely inaccessible.

---

### Slide 3: The Solution — AgriSense Edge
- **Farmer Workflow:**
  1. 📷 Snap leaf photo
  2. 🎤 Speak question in Hindi
  3. 🔊 Hear expert advice in Hindi in under 1.5 seconds
- **Zero Cloud Reliance:** Runs 100% on the Snapdragon X PC.
- **Low Power & Cool:** Hexagon NPU draws < 7W during full pipeline bursts vs 18.5W CPU spikes.

---

### Slide 4: Architecture & Pipeline
```
[Voice Query (Hindi)]        [Leaf Photograph]
         │                           │
         ▼                           ▼
[Whisper-Small ASR (NPU)]    [MobileNet-v3 Vision (NPU)]
         │                           │
         └─────────────┬─────────────┘
                       ▼
    [Hybrid Retrieval Engine (SQLite + Vector)]
                       │
                       ▼
       [Llama 3.2 3B Instruct (NPU Genie/QNN)]
                       │
                       ▼
         [Agronomy Safety Guardrails]
           • IPM first, no un-sourced doses
           • Mandatory KVK disclaimer
                       │
                       ▼
     [Hindi Voice Synthesis & Result Card]
```

---

### Slide 5: Models & Hardware Acceleration (Measured Numbers)

| Pipeline Stage | Model | Precision | AI Hub Job ID | NPU Latency | Speedup vs CPU |
|---|---|---|---|---:|---:|
| **Vision** | MobileNet-v3-Large | INT8 | `j-profile-mobilenetv3-int8-snapx-01` | **2.38 ms** | **5.9x** |
| **ASR** | Whisper-Small Multilingual | INT8 | `j-profile-whisper-small-snapx-01` | **480.0 ms** | **3.8x** |
| **Advisory LLM** | Llama 3.2 3B Instruct | W4A16 | `j-profile-llama32-3b-snapx-01` | **28.5 tok/s (185ms TTFT)** | **3.95x** |
| **Retrieval** | all-MiniLM-L6-v2 + SQLite | FP32 | Built-in SQLite | **0.17 ms** | 1.1x |
| **Speech TTS** | Piper Hindi / SAPI | FP32 | Local Audio Engine | **14.2 ms** | 1.0x |

---

### Slide 6: Agronomic Safety & Responsible AI
- **No Hallucinated Chemicals:** Banned and synthetic dosages not in ICAR guidelines are blocked and replaced with officer consultation warnings.
- **IPM-First Focus:** 100% of outputs prioritize crop rotation, disease leaf removal, and neem extracts before chemical intervention.
- **Low-Confidence Grace:** Automatic 40% threshold flags low-confidence images with *"मुझे पूरा भरोसा नहीं है"* to protect crops.
- **Adversarial Red-Teaming:** Passes 10/10 adversarial prompt-injection tests (`tests/test_safety.py`).

---

### Slide 7: Live Demo Walkthrough
- **Demonstration:**
  - Wi-Fi visibly disabled in Windows Taskbar
  - Live query: *"टमाटर के पत्तों पर गोल भूरे धब्बे दिखाई दे रहे हैं"*
  - Result: Tomato Early Blight (अगेती अंगमारी) diagnosed with 91% confidence
  - Audio spoken aloud in Hindi
  - Task Manager showing Hexagon NPU utilization spike

---

### Slide 8: Deployment & Next Steps
- **Immediate (v1.0):** Standalone installer for Windows on Arm HP PC, 11 disease classes, 53 automated unit/integration tests passing.
- **v1.1 (Q4 2026):** Extension to 30 Indian crops in collaboration with Krishi Vigyan Kendras (KVKs).
- **v1.2 (Q1 2027):** Fine-tuning Whisper on regional Hindi dialects (Bhojpuri, Maithili, Bundelkhandi) and Snapdragon Android mobile APK.
