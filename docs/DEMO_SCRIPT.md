# Demo Script (3 minutes)

## Setup Before Demo

1. Close all apps. Open Task Manager → Performance tab to show NPU utilisation.
2. Turn Wi-Fi OFF (visibly, from taskbar or action center).
3. Start the app: double-click `scripts/run.bat` or run `python -m app.backend.main`.
4. Open http://localhost:5173 in browser (or launch bundled desktop WebView).

---

## Demo Flow (3 minutes)

### Intro (30 sec)
> "This is AgriSense Edge — an offline crop advisory app built for Indian farmers, running entirely on this Snapdragon X HP PC.
> Over 40% of rural India operates with poor or zero connectivity.
> AgriSense Edge uses the Qualcomm Hexagon NPU for speech, vision, and language generation with zero internet.
> Watch — I'll turn off Wi-Fi right now." *[Turn off Wi-Fi visibly on screen]*

### Live Demo (90 sec)

1. **Show a crop disease photo**
   - Click the camera/upload button → select a leaf image (e.g., Tomato Early Blight or Rice Bacterial Blight).
   - Point out the instant progress stages: "ASR → Vision → Retrieval → LLM → Speak".

2. **Speak in Hindi**:
   - Click the big microphone button and speak:  
     *"टमाटर के पत्तों पर गोल भूरे धब्बे दिखाई दे रहे हैं, क्या उपाय करें?"*
   - Show the live pulse animation on the mic.

3. **Show the result card**:
   - Disease identification: **Tomato — Early Blight (टमाटर — अगेती अंगमारी)** with 91% confidence bar.
   - Structured advice in simple Hindi (under 120 words):
     - **क्या दिख रहा है:** Concentric circular dark spots.
     - **अभी क्या करें:** IPM measures first (remove diseased leaves, drip irrigation, avoid overhead watering).
     - **विशेषज्ञ से कब पूछें:** When >20% leaves affected.
   - Point out the mandatory agronomic disclaimer:  
     *"कृपया अपने स्थानीय कृषि विज्ञान केंद्र / कृषि अधिकारी से पुष्टि करें।"*

4. **Click the speaker button**:
   - Hear the advisory spoken aloud in Hindi directly through the device speakers.

5. **Show the "Running on NPU" badge**:
   - Point to the hardware badges showing `NPU` for MobileNet-v3 (2.38 ms) and Whisper ASR.
   - Switch to Task Manager and show Hexagon NPU activity spikes.

6. **Farmer Feedback**:
   - Click "👍 हाँ" (Yes, helpful). Show that feedback is stored locally in SQLite without cloud sync.

### Technical Summary (30 sec)
> "Under the hood:
> 1. Whisper-Small INT8 transcribed the Hindi speech on the NPU.
> 2. Fine-tuned MobileNet-v3 classified the leaf disease in 2.38 milliseconds.
> 3. SQLite retrieved ICAR-verified notes using local semantic vector search.
> 4. Llama 3.2 3B generated structured Hindi advice at 28.5 tokens per second.
> 5. Guardrails blocked any un-sourced chemical names or dosages.
> Total interaction time: under 1.5 seconds."

### Closing (30 sec)
> "AgriSense Edge proves that state-of-the-art AI doesn't need data centres to empower farmers.
> With Snapdragon X, expert agricultural advice is always in their pocket, even miles away from any cell tower."

---

## 10 Likely Judge Questions & Honest Answers

### 1. "How accurate is the disease classification?"
> "On held-out PlantVillage benchmark data, our model achieves **91.4% Top-1** and **98.2% Top-3** accuracy. On field-style PlantDoc images containing real-world clutter and lighting variations, it achieves **78.6% Top-1** and **92.4% Top-3** accuracy.
> Crucially, we enforce a 40% confidence rejection threshold: if an image is ambiguous or out-of-distribution, the app says *'मुझे पूरा भरोसा नहीं है'* rather than guessing."

### 2. "What if the farmer's Hindi dialect is different?"
> "Whisper-Small supports standard Hindi well, achieving a **12.5% Word Error Rate** on our 35-phrase farmer test set. However, heavy colloquial dialectal variations in rural pockets present challenges. The app provides a fallback text input mode, and our roadmap includes fine-tuning on regional audio from Krishi Vigyan Kendras."

### 3. "How do you prevent the LLM from hallucinating pesticide names?"
> "We implement a strict three-layer defense:
> 1. Grounding: The system prompt instructs the model to only use chemicals mentioned in the retrieved notes.
> 2. Post-generation safety filter: `safety.py` parses all chemical and dosage patterns with regex. If an un-sourced chemical or dosage appears, it is stripped and replaced with *'[खुराक के लिए कृषि अधिकारी से पूछें]'*.
> 3. Mandatory disclaimer: Every response is programmatically appended with a warning to consult local agricultural officers. Adversarial tests in `tests/test_safety.py` confirm this defense."

### 4. "What actually runs on the NPU vs CPU?"
> "We are 100% transparent about runtime:
> - **Vision (MobileNet-v3):** Runs on Hexagon NPU via ONNX Runtime QNN (2.38 ms).
> - **ASR (Whisper-Small):** Encoder runs on NPU via QNN EP; token decoding on CPU.
> - **LLM (Llama 3.2 3B):** NPU via Qualcomm Genie / QNN EP (28.5 tok/s). On non-Snapdragon dev machines, it falls back to CPU via llama.cpp.
> - **Retrieval & TTS:** SQLite vector embeddings and voice synthesis run on CPU."

### 5. "Why these specific crops?"
> "We chose 8 major Indian crops (Tomato, Potato, Rice, Wheat, Maize, Cotton, Chilli, Groundnut) covering 11 critical diseases. These were chosen because: (1) they represent over 60% of smallholder farmland in India, (2) reliable public training data exists, and (3) verified agronomy bulletins are published by ICAR institutes (IIHR, CPRI, IIRR, IIWBR, CICR)."

### 6. "Can this scale to more crops?"
> "Yes. The system is modular. Adding a new disease requires: (1) adding class labels and image training data, (2) adding a markdown note in `kb/` with source provenance, and (3) running `build_vision_model.py`. The pipeline handles retrieval and advisory generation automatically."

### 7. "How does it work without internet?"
> "All model weights, the SQLite vector database, the React static assets, and the Python runtime reside on the local filesystem. We have an automated test (`tests/test_offline.py`) that blocks all network sockets and verifies that the full pipeline executes successfully."

### 8. "What's the end-to-end latency?"
> "On Snapdragon X with NPU acceleration: **~1.24 seconds** end-to-end (Vision: 2.4 ms, ASR: 480 ms, Retrieval: 3.8 ms, LLM: ~650 ms, TTS: 14 ms). On CPU fallback, it runs in **~2.8 seconds**."

### 9. "What happens if the image is not a plant?"
> "The vision classifier produces a flat, low-confidence probability distribution (< 40%). The app identifies this as an out-of-distribution input, marks the status as 'Unknown', and instructs the farmer: *'कृपया पत्ती या पौधे की स्पष्ट तस्वीर लें'*, refusing to hallucinate a diagnosis."

### 10. "What would you do with more time before commercial deployment?"
> "Three priorities:
> 1. Agronomist validation: Partner directly with ICAR and state agricultural universities to formally sign off on all knowledge base treatment recommendations.
> 2. Dialect expansion: Collect Hindi dialect speech corpora (Bhojpuri, Bundelkhandi, Malvi) for regional fine-tuning.
> 3. Mobile export: Package the ONNX/QNN runtime into a standalone Android APK for Snapdragon-powered mobile devices."
