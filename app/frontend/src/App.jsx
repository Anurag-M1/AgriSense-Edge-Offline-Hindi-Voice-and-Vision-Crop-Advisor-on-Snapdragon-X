import { useState, useRef, useCallback } from 'react'
import './index.css'

const STAGES = [
  { key: 'asr', label_hi: 'वाणी', label_en: 'Speech' },
  { key: 'vision', label_hi: 'छवि', label_en: 'Vision' },
  { key: 'retrieval', label_hi: 'खोज', label_en: 'Search' },
  { key: 'llm', label_hi: 'सलाह', label_en: 'Advice' },
  { key: 'tts', label_hi: 'बोलना', label_en: 'Speak' },
]

const TRANSLATIONS = {
  hi: {
    title: 'एग्रीसेंस एज',
    subtitle: 'ऑफ़लाइन फ़सल सलाहकार',
    mic_label: 'बोलें',
    camera_label: 'फ़ोटो लें',
    upload_label: 'फ़ोटो चुनें',
    submit_label: 'जाँच करें',
    result_title: 'परिणाम',
    confidence: 'विश्वास',
    helpful_q: 'क्या यह सलाह उपयोगी थी?',
    yes: 'हाँ',
    no: 'नहीं',
    processing: 'जाँच हो रही है...',
    ready: 'तैयार है',
    speak_btn: 'सुनें',
    toggle_lang: 'English',
    text_placeholder: 'यहाँ टाइप करें...',
  },
  en: {
    title: 'AgriSense Edge',
    subtitle: 'Offline Crop Advisory',
    mic_label: 'Speak',
    camera_label: 'Take Photo',
    upload_label: 'Upload Photo',
    submit_label: 'Diagnose',
    result_title: 'Result',
    confidence: 'Confidence',
    helpful_q: 'Was this advice helpful?',
    yes: 'Yes',
    no: 'No',
    processing: 'Processing...',
    ready: 'Ready',
    speak_btn: 'Listen',
    toggle_lang: 'हिन्दी',
    text_placeholder: 'Type here...',
  },
}

function App() {
  const [lang, setLang] = useState('hi')
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [textInput, setTextInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStage, setCurrentStage] = useState(null)
  const [stageStatuses, setStageStatuses] = useState({})
  const [result, setResult] = useState(null)
  const [feedbackSent, setFeedbackSent] = useState(false)

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const fileInputRef = useRef(null)

  const t = TRANSLATIONS[lang]

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setImage(file)
      const reader = new FileReader()
      reader.onload = (ev) => setImagePreview(ev.target.result)
      reader.readAsDataURL(file)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      audioChunksRef.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setAudioBlob(blob)
        stream.getTracks().forEach((t) => t.stop())
      }

      recorder.start()
      mediaRecorderRef.current = recorder
      setIsRecording(true)
    } catch (err) {
      console.error('Mic access denied:', err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleSubmit = async () => {
    if (!image && !audioBlob && !textInput) return

    setIsProcessing(true)
    setResult(null)
    setFeedbackSent(false)
    setStageStatuses({})

    const formData = new FormData()
    if (image) formData.append('image', image)
    if (audioBlob) formData.append('audio', audioBlob, 'recording.wav')
    if (textInput) formData.append('text_input', textInput)

    try {
      // Simulate stage progress
      for (const stage of STAGES) {
        setCurrentStage(stage.key)
        setStageStatuses((prev) => ({ ...prev, [stage.key]: 'active' }))
        await new Promise((r) => setTimeout(r, 200))
        setStageStatuses((prev) => ({ ...prev, [stage.key]: 'done' }))
      }

      const response = await fetch('/api/diagnose', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()

      // Update stage statuses from actual response
      const newStatuses = {}
      data.stages?.forEach((s) => {
        newStatuses[s.stage] = s.status === 'ok' ? 'done' : 'error'
      })
      setStageStatuses(newStatuses)
      setResult(data)
    } catch (err) {
      console.error('Diagnosis failed:', err)
      setResult({
        disease_label: 'Error',
        confidence: 0,
        advice_text: `त्रुटि हुई: ${err.message}`,
        stages: [],
        total_latency_ms: 0,
        tts_available: false,
      })
    } finally {
      setIsProcessing(false)
      setCurrentStage(null)
    }
  }

  const handleFeedback = async (helpful) => {
    if (!result?.case_id) return
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: result.case_id, helpful }),
      })
      setFeedbackSent(true)
    } catch (err) {
      console.error('Feedback failed:', err)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-6 max-w-lg mx-auto">
      {/* Header */}
      <header className="w-full flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-primary-light">{t.title}</h1>
          <p className="text-sm text-muted">{t.subtitle}</p>
        </div>
        <button
          onClick={() => setLang(lang === 'hi' ? 'en' : 'hi')}
          className="text-sm px-3 py-1.5 rounded-lg border border-white/20 hover:bg-white/10 transition touch-target"
        >
          {t.toggle_lang}
        </button>
      </header>

      {/* Image upload / preview */}
      <div className="w-full glass-card p-4 mb-4">
        {imagePreview ? (
          <div className="relative">
            <img
              src={imagePreview}
              alt="Crop"
              className="w-full h-48 object-cover rounded-lg"
            />
            <button
              onClick={() => { setImage(null); setImagePreview(null) }}
              className="absolute top-2 right-2 bg-black/60 text-white rounded-full w-8 h-8 flex items-center justify-center text-lg"
            >
              ×
            </button>
          </div>
        ) : (
          <div className="flex gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 py-4 rounded-xl bg-primary/20 border-2 border-dashed border-primary/40 hover:bg-primary/30 transition flex flex-col items-center gap-2 touch-target"
            >
              <span className="text-3xl">📷</span>
              <span className="text-sm">{t.upload_label}</span>
            </button>
          </div>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleImageUpload}
          className="hidden"
        />
      </div>

      {/* Audio / text input */}
      <div className="w-full glass-card p-4 mb-4">
        <div className="flex items-center gap-3">
          {/* Mic button */}
          <button
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            className={`relative w-16 h-16 rounded-full flex items-center justify-center text-2xl transition touch-target ${
              isRecording
                ? 'bg-danger mic-pulse scale-110'
                : 'bg-primary hover:bg-primary-dark'
            }`}
          >
            🎤
          </button>

          {/* Text input */}
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder={t.text_placeholder}
            className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:border-primary touch-target"
          />
        </div>
        {audioBlob && (
          <p className="mt-2 text-xs text-primary-light">✅ ऑडियो रिकॉर्ड हो गया</p>
        )}
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={isProcessing || (!image && !audioBlob && !textInput)}
        className="w-full py-4 rounded-xl bg-primary font-semibold text-lg text-white disabled:opacity-40 hover:bg-primary-dark transition mb-4 touch-target"
      >
        {isProcessing ? t.processing : t.submit_label}
      </button>

      {/* Stage progress */}
      {isProcessing && (
        <div className="w-full glass-card p-4 mb-4">
          <div className="flex items-center justify-between">
            {STAGES.map((stage, i) => (
              <div key={stage.key} className="flex flex-col items-center gap-1">
                <div className={`stage-dot ${stageStatuses[stage.key] || 'pending'}`} />
                <span className="text-xs text-muted">
                  {lang === 'hi' ? stage.label_hi : stage.label_en}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Result card */}
      {result && (
        <div className="w-full glass-card p-5 mb-4">
          <h2 className="text-lg font-bold mb-3 text-primary-light">{t.result_title}</h2>

          {/* Disease label */}
          <div className="mb-3">
            <p className="text-xl font-semibold">
              {result.disease_label?.replace(/___/g, ' — ') || 'Unknown'}
            </p>
          </div>

          {/* Confidence bar */}
          <div className="mb-4">
            <div className="flex justify-between text-xs text-muted mb-1">
              <span>{t.confidence}</span>
              <span>{Math.round((result.confidence || 0) * 100)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-3">
              <div
                className="confidence-bar"
                style={{ width: `${Math.max(5, (result.confidence || 0) * 100)}%` }}
              />
            </div>
          </div>

          {/* Advice text */}
          <div className="bg-white/5 rounded-xl p-4 mb-3 leading-relaxed whitespace-pre-wrap text-sm">
            {result.advice_text || 'No advice generated.'}
          </div>

          {/* Stage backend badges */}
          {result.stages?.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {result.stages.map((s) => (
                <span
                  key={s.stage}
                  className={`backend-badge ${s.backend?.includes('npu') ? 'npu' : 'cpu'}`}
                >
                  {s.stage}: {s.backend} ({s.latency_ms}ms)
                </span>
              ))}
            </div>
          )}

          {/* TTS / speak button */}
          {result.tts_available && (
            <button className="w-full py-3 rounded-xl bg-primary/20 border border-primary/40 hover:bg-primary/30 transition flex items-center justify-center gap-2 touch-target mb-3">
              <span className="text-xl">🔊</span>
              <span>{t.speak_btn}</span>
            </button>
          )}

          {/* Feedback */}
          {!feedbackSent ? (
            <div className="border-t border-white/10 pt-3">
              <p className="text-sm text-muted mb-2">{t.helpful_q}</p>
              <div className="flex gap-3">
                <button
                  onClick={() => handleFeedback(true)}
                  className="flex-1 py-2 rounded-lg bg-primary/20 hover:bg-primary/30 transition touch-target"
                >
                  👍 {t.yes}
                </button>
                <button
                  onClick={() => handleFeedback(false)}
                  className="flex-1 py-2 rounded-lg bg-danger/20 hover:bg-danger/30 transition touch-target"
                >
                  👎 {t.no}
                </button>
              </div>
            </div>
          ) : (
            <p className="text-sm text-primary-light text-center pt-3 border-t border-white/10">
              ✅ धन्यवाद!
            </p>
          )}

          {/* Latency */}
          <p className="text-xs text-muted text-right mt-2">
            Total: {Math.round(result.total_latency_ms || 0)}ms
          </p>
        </div>
      )}

      {/* Footer */}
      <footer className="text-xs text-muted text-center mt-auto pt-4">
        <p>AgriSense Edge v0.1 • ऑफ़लाइन • Qualcomm Snapdragon AI</p>
      </footer>
    </div>
  )
}

export default App
