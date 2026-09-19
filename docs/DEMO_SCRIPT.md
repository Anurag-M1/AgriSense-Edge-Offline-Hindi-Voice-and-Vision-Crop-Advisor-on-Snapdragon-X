# Demo Script (3 minutes)

## Setup Before Demo

1. Close all apps. Open Task Manager → Performance tab to show NPU utilisation.
2. Turn Wi-Fi OFF (visibly, from taskbar).
3. Start the app: double-click `run.bat` or run `python -m app.backend.main`.
4. Open http://localhost:5173 in Edge browser.

## Demo Flow (3 min)

### Intro (30 sec)
> "This is AgriSense Edge — an offline crop advisory for Indian farmers.
> It runs entirely on this Snapdragon X laptop, using the NPU for AI inference.
> Watch — I'll turn off Wi-Fi now." *[Turn off Wi-Fi visibly]*

### Live Demo (90 sec)

1. **Show a tomato leaf image** (use the sample image in `demo/sample_tomato_blight.jpg`)
   - Click the camera icon → upload the image
   - Point out the progress ticks: "ASR... Vision... Retrieval... LLM... TTS..."

2. **Speak in Hindi**: "इस पत्ती में क्या बीमारी है?" (What disease does this leaf have?)
   - Click the mic button and speak

3. **Show the result card**:
   - Disease name with confidence bar
   - Hindi advice: what it looks like → what to do → when to ask an expert
   - Point out the safety disclaimer: "अपने स्थानीय कृषि विज्ञान केंद्र से पुष्टि करें"

4. **Click the speaker button** — hear the advice spoken in Hindi

5. **Show the "was this helpful?" feedback** — click yes

6. **Show Task Manager** — point out NPU utilisation during inference

### Technical Summary (30 sec)
> "Under the hood: Whisper for Hindi speech recognition, MobileNet for disease detection,
> Llama 3.2 for generating the advice — all running on the NPU via Qualcomm's QNN runtime.
> End-to-end latency is [X] seconds. The knowledge base is sourced from ICAR and state
> agriculture departments. Safety guardrails prevent the AI from inventing chemical names."

### Closing (30 sec)
> "40% of rural India is offline. AgriSense Edge puts expert crop advisory in farmers' hands
> without needing internet. The NPU makes it fast enough for real-time use."

---

## 10 Likely Judge Questions & Honest Answers

### 1. "How accurate is the disease classification?"
> "On held-out PlantVillage data: [X]% top-1 accuracy. On field-style PlantDoc images: [X]%.
> The model has a rejection threshold — when confidence is below [X]%, it says 'I'm not sure'
> rather than guessing. Lab images generalise imperfectly to field conditions; we report both numbers."

### 2. "What if the farmer's Hindi dialect is different?"
> "Whisper-Small supports Hindi broadly but struggles with heavy dialectal variation.
> We measured WER of [X]% on our test set. For production, fine-tuning on regional dialect data
> would improve this. The app also has a text input fallback."

### 3. "How do you prevent the LLM from hallucinating pesticide names?"
> "Three layers: (1) The prompt grounds answers only in retrieved knowledge base entries.
> (2) A post-processing safety module blocks any chemical name not present in the retrieved notes.
> (3) Every response includes a disclaimer to confirm with a local agriculture officer.
> We have adversarial tests that verify these guardrails."

### 4. "What actually runs on the NPU vs CPU?"
> *[Show the model table in README]* "Vision and ASR run on NPU via QNN EP.
> The LLM runs on [NPU via Genie / CPU via llama.cpp — state actual].
> TTS and embeddings run on CPU. We label each clearly."

### 5. "Why these specific crops?"
> "We selected 8 crops — tomato, potato, rice, wheat, maize, cotton, chilli, groundnut —
> because (1) they cover a large share of Indian agriculture, (2) public training data exists,
> and (3) ICAR has published disease management guidelines for them."

### 6. "Can this scale to more crops?"
> "Yes. The architecture is modular: add images to the training set, add a knowledge base entry,
> and retrain. The bottleneck is curated agronomic content, not the model."

### 7. "How does it work without internet?"
> "All models and the knowledge base are bundled locally. No API calls.
> We have an automated test (`test_offline.py`) that blocks all network sockets and runs
> the full pipeline to prove it."

### 8. "What's the end-to-end latency?"
> "[X] seconds on Snapdragon X with NPU, [Y] seconds CPU-only. Breakdown: ASR [X]ms,
> Vision [X]ms, Retrieval [X]ms, LLM [X]ms, TTS [X]ms."

### 9. "What happens if the image is not a plant?"
> "The classifier returns low confidence for out-of-distribution inputs.
> Below the threshold, the app shows 'I cannot identify this — please take a clearer photo
> of the affected leaf.' It does not guess."

### 10. "What would you do with more time?"
> "Three things: (1) Fine-tune Whisper on regional Hindi dialects, (2) add more crops
> with agronomist-reviewed content, (3) build a federated learning loop so the model improves
> from farmer feedback without centralising data."
