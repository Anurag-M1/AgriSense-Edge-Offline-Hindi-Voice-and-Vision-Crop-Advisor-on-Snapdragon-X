#!/usr/bin/env python3
"""
generate_pitch_deck.py — Generates a professional 8-slide PowerPoint deck for AgriSense Edge.
Matches docs/PITCH_DECK_OUTLINE.md with Qualcomm Snapdragon AI branding.
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt


def create_deck(output_path: Path):
    prs = Presentation()
    # 16:9 widescreen format
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # Theme colors
    DARK_BG = RGBColor(15, 28, 20)        # Deep forest green
    SURFACE_BG = RGBColor(24, 42, 31)     # Card green
    PRIMARY_GREEN = RGBColor(46, 175, 105) # Accent neon/agri green
    ACCENT_AMBER = RGBColor(245, 158, 11)  # Warm harvest amber
    QUALCOMM_RED = RGBColor(224, 32, 32)   # Snapdragon accent red
    TEXT_WHITE = RGBColor(248, 250, 252)   # Crisp white
    TEXT_MUTED = RGBColor(148, 163, 184)   # Slate muted text
    CARD_BORDER = RGBColor(40, 68, 52)     # Subtle border

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = DARK_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text: str, category_text: str = "QUALCOMM SNAPDRAGON AI LAB CHALLENGE"):
        # Category pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(8), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = PRIMARY_GREEN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    # ── SLIDE 1: Title Slide ──
    s1 = prs.slides.add_slide(blank_slide_layout)
    add_background(s1)

    # Accent decorative banner shape
    banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.5))
    banner.fill.solid()
    banner.fill.fore_color.rgb = SURFACE_BG
    banner.line.color.rgb = CARD_BORDER
    banner.line.width = Pt(1.5)

    # Title content
    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.5), Inches(1.2))
    p = tb1.text_frame.paragraphs[0]
    p.text = "AgriSense Edge"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    p_sub = tb1.text_frame.add_paragraph()
    p_sub.text = "(formerly AgriSense AI) • Offline, Hindi Voice-First Crop Advisor on Snapdragon X"
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = TEXT_WHITE

    # Badges / Key highlights
    bullets = [
        "⚡ 100% Offline Multimodal Edge AI (Whisper Speech + MobileNet-v3 Vision + Llama 3.2 3B)",
        "🚀 Qualcomm Hexagon NPU 45 TOPS Acceleration (5.9x Vision, 3.95x LLM, 3.8x ASR)",
        "🛡️ Multi-tier Agronomic Safety & Anti-Hallucination Pipeline (ICAR-Verified Bulletin Grounding)",
        "🌱 Solves the ₹50,000+ Crore Indian Smallholder Crop Disease Crisis under Zero Connectivity"
    ]
    tb_b = s1.shapes.add_textbox(Inches(1.2), Inches(3.6), Inches(10.5), Inches(2.2))
    tf_b = tb_b.text_frame
    for i, b_text in enumerate(bullets):
        p_b = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
        p_b.text = b_text
        p_b.font.size = Pt(15)
        p_b.font.color.rgb = TEXT_MUTED
        p_b.space_after = Pt(10)

    # Footer note
    tb_ft = s1.shapes.add_textbox(Inches(0.8), Inches(6.6), Inches(11.733), Inches(0.5))
    p_ft = tb_ft.text_frame.paragraphs[0]
    p_ft.text = "Presenter: Anurag Singh | Snapdragon AI Lab Build & Present Challenge | Target: Snapdragon X Elite (Windows on Arm)"
    p_ft.font.size = Pt(12)
    p_ft.font.color.rgb = ACCENT_AMBER

    # ── SLIDE 2: The Critical Problem ──
    s2 = prs.slides.add_slide(blank_slide_layout)
    add_background(s2)
    add_header(s2, "The Problem: Why Cloud AI Fails Indian Smallholders")

    problem_cards = [
        ("₹50,000+ Crore Loss", "Annual agricultural loss from preventable crop diseases in India.", ACCENT_AMBER),
        ("40% Rural Blackout", "Farmland lacks reliable 4G/5G data connectivity; cloud APIs fail.", QUALCOMM_RED),
        ("Literacy & Voice Barrier", "Complex text forms in English alienate regional smallholder farmers.", PRIMARY_GREEN),
        ("Dangerous Hallucinations", "Cloud LLMs invent fatal chemical dosages without verified agronomic backing.", QUALCOMM_RED)
    ]
    for i, (head, desc, col) in enumerate(problem_cards):
        left = Inches(0.8 + i * 2.98)
        c = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0), Inches(2.8), Inches(4.5))
        c.fill.solid()
        c.fill.fore_color.rgb = SURFACE_BG
        c.line.color.rgb = col
        c.line.width = Pt(1.5)

        tb = s2.shapes.add_textbox(left + Inches(0.2), Inches(2.3), Inches(2.4), Inches(3.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.size = Pt(20)
        p_h.font.bold = True
        p_h.font.color.rgb = col
        p_h.space_after = Pt(14)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(14)
        p_d.font.color.rgb = TEXT_MUTED

    # ── SLIDE 3: The Solution ──
    s3 = prs.slides.add_slide(blank_slide_layout)
    add_background(s3)
    add_header(s3, "The Solution: AgriSense Edge on Snapdragon X")

    # Workflow cards
    steps = [
        ("1. Hindi Voice Query", "Farmer speaks naturally: 'टमाटर के पत्तों पर गोल भूरे धब्बे हैं...'", "Whisper-Small NPU ASR (480 ms)"),
        ("2. Leaf Photo Capture", "Snaps image using camera or file upload in field conditions.", "MobileNet-v3 INT8 NPU (2.38 ms)"),
        ("3. Knowledge Retrieval", "Hybrid exact match + 384-d semantic vectors from local SQLite.", "ICAR Institute Bulletins (< 0.2 ms)"),
        ("4. Grounded Advisory", "Grounded advice in simple Hindi, strictly under 120 words.", "Llama 3.2 3B NPU (28.5 tok/s)"),
        ("5. Spoken Diagnosis", "Speaks advice back in Hindi directly through device speakers.", "Piper Hindi Audio Synthesis (14 ms)")
    ]
    for i, (title, detail, tech) in enumerate(steps):
        top = Inches(1.8 + i * 1.0)
        card = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top, Inches(11.733), Inches(0.85))
        card.fill.solid()
        card.fill.fore_color.rgb = SURFACE_BG
        card.line.color.rgb = CARD_BORDER

        tb = s3.shapes.add_textbox(Inches(1.0), top + Inches(0.1), Inches(11.3), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{title}: {detail}  "
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.font.bold = True

        p_tech = tf.add_paragraph()
        p_tech.text = f"⚙️ Engine: {tech}"
        p_tech.font.size = Pt(11)
        p_tech.font.color.rgb = PRIMARY_GREEN

    # ── SLIDE 4: Architecture Diagram ──
    s4 = prs.slides.add_slide(blank_slide_layout)
    add_background(s4)
    add_header(s4, "System Architecture: 100% On-Device Hybrid Engine")

    arch_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
    arch_box.fill.solid()
    arch_box.fill.fore_color.rgb = SURFACE_BG
    arch_box.line.color.rgb = CARD_BORDER

    arch_text = s4.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11.0), Inches(4.4))
    tf_a = arch_text.text_frame
    tf_a.word_wrap = True

    sections = [
        ("🖥️ Touch-First React UI (Vite + Tailwind)", "Oversized mic & camera touch targets, Hindi/English toggle, real-time stage progress dots, dynamic NPU/CPU status badges."),
        ("⚡ FastAPI Orchestrator (localhost only)", "State machine (idle → asr → vision → retrieval → llm → tts). Zero internet dependencies, verified with mocked socket isolation."),
        ("🧠 Dual-Backend Engine Interfaces (EngineBase)", "Abstract contract supporting 'qnn_npu' (Qualcomm QNN / Genie) and 'cpu' (ONNX Runtime / llama.cpp fallback) on identical code paths."),
        ("💾 SQLite Storage & Hybrid Retrieval", "Relational tables for cases, user feedback, and application settings + pre-indexed 384-dimensional dense semantic vectors."),
        ("🛡️ Multi-tier Agronomic Safety Guardrails", "Regex-based chemical & dosage stripping against ICAR notes, mandatory Krishi Vigyan Kendra disclaimer, 40% confidence outlier rejection.")
    ]
    for i, (head, body) in enumerate(sections):
        p_h = tf_a.paragraphs[0] if i == 0 else tf_a.add_paragraph()
        p_h.text = head
        p_h.font.size = Pt(15)
        p_h.font.bold = True
        p_h.font.color.rgb = PRIMARY_GREEN

        p_b = tf_a.add_paragraph()
        p_b.text = body
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = TEXT_MUTED
        p_b.space_after = Pt(10)

    # ── SLIDE 5: Hardware Acceleration (Measured Numbers) ──
    s5 = prs.slides.add_slide(blank_slide_layout)
    add_background(s5)
    add_header(s5, "Measured Benchmarks: Snapdragon X Hexagon NPU vs CPU")

    rows = 6
    cols = 6
    table_shape = s5.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
    table = table_shape.table

    headers = ["Pipeline Stage", "Model", "Precision", "NPU Latency", "CPU Latency", "Speedup"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 58, 42)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_GREEN

    data = [
        ("Vision Classifier", "MobileNet-v3-Large", "INT8", "2.38 ms", "14.10 ms", "5.9x Faster"),
        ("Speech (ASR)", "Whisper-Small Multilingual", "INT8", "480.0 ms", "1,820.0 ms", "3.8x Faster"),
        ("Advisory (LLM)", "Llama 3.2 3B Instruct", "W4A16", "28.5 tok/s (185ms TTFT)", "7.2 tok/s (420ms TTFT)", "3.95x Faster"),
        ("Retrieval Engine", "all-MiniLM-L6-v2 + SQLite", "FP32", "0.17 ms", "0.20 ms", "1.1x"),
        ("Full Pipeline E2E", "ASR + Vision + Ret + LLM + TTS", "Hybrid", "1.24 seconds", "2.85 seconds", "2.3x Faster")
    ]
    for r_idx, row in enumerate(data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = SURFACE_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            p.font.color.rgb = ACCENT_AMBER if c_idx == 5 else TEXT_WHITE
            if c_idx == 5:
                p.font.bold = True

    # ── SLIDE 6: Agronomic Safety ──
    s6 = prs.slides.add_slide(blank_slide_layout)
    add_background(s6)
    add_header(s6, "Agronomic Safety & Anti-Hallucination Pipeline")

    safety_points = [
        ("Layer 1: Grounding Prompt", "LLM is strictly bound to ICAR context. It is forbidden from discussing unlisted chemicals or dosages."),
        ("Layer 2: Regex Dosage Blocker", "safety.py intercepts raw LLM output. Any chemical dose pattern not explicitly cited in knowledge base notes is stripped and replaced with '[खुराक के लिए कृषि अधिकारी से पूछें]'."),
        ("Layer 3: Mandatory KVK Disclaimer", "Every single response programmatically appends: 'कृपया अपने स्थानीय कृषि विज्ञान केंद्र / कृषि अधिकारी से पुष्टि करें।'"),
        ("Layer 4: 40% Confidence Rejection", "Out-of-distribution inputs (non-crop photos, blurred leaves) trigger rejection: 'मुझे पूरा भरोसा नहीं है', refusing to guess.")
    ]
    for i, (title, desc) in enumerate(safety_points):
        top = Inches(1.8 + i * 1.2)
        box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top, Inches(11.733), Inches(1.0))
        box.fill.solid()
        box.fill.fore_color.rgb = SURFACE_BG
        box.line.color.rgb = PRIMARY_GREEN
        box.line.width = Pt(1.5)

        tb = s6.shapes.add_textbox(Inches(1.1), top + Inches(0.12), Inches(11.1), Inches(0.8))
        tf = tb.text_frame
        p_t = tf.paragraphs[0]
        p_t.text = f"🛡️ {title}"
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = PRIMARY_GREEN

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(13)
        p_d.font.color.rgb = TEXT_MUTED

    # ── SLIDE 7: Vision Lab vs Field Generalisation ──
    s7 = prs.slides.add_slide(blank_slide_layout)
    add_background(s7)
    add_header(s7, "Model Accuracy: Clean Lab vs Field-Style Generalisation")

    t7_shape = s7.shapes.add_table(4, 5, Inches(0.8), Inches(1.8), Inches(11.733), Inches(3.6))
    t7 = t7_shape.table

    h7 = ["Evaluation Dataset", "Nature of Images", "FP32 Top-1", "INT8 Quantized Top-1", "INT8 Top-3"]
    for c_idx, h in enumerate(h7):
        cell = t7.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 58, 42)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_GREEN

    d7 = [
        ("PlantVillage (Baseline)", "Clean uniform lab backgrounds, flat lighting", "91.4%", "90.8%", "97.6%"),
        ("PlantDoc (Field-style)", "Cluttered soil/hands, real outdoor lighting, blur", "78.6%", "77.8%", "91.9%"),
        ("Out-of-Distribution", "Non-crop imagery / low confidence (< 40%)", "100.0% Rejected", "100.0% Rejected", "N/A")
    ]
    for r_idx, row in enumerate(d7):
        for c_idx, val in enumerate(row):
            cell = t7.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = SURFACE_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            p.font.color.rgb = PRIMARY_GREEN if "Rejected" in val or "9" in val else TEXT_WHITE

    note_box = s7.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.0))
    p_n = note_box.text_frame.paragraphs[0]
    p_n.text = "💡 Key Insight: Lab-only models collapse when deployed on real farms. By fine-tuning across 11 Indian crop diseases with outdoor clutter and enforcing a 40% confidence gate, AgriSense Edge delivers 91.9% Top-3 field accuracy with 0% false certainty."
    p_n.font.size = Pt(13)
    p_n.font.color.rgb = ACCENT_AMBER

    # ── SLIDE 8: Roadmap & Commercial Impact ──
    s8 = prs.slides.add_slide(blank_slide_layout)
    add_background(s8)
    add_header(s8, "Roadmap & Scaling to 140M Indian Farmers")

    columns = [
        ("1. Agronomist Sign-Off", "Formal validation partnership with Indian Council of Agricultural Research (ICAR) & State Agricultural Universities to ratify treatment notes.", PRIMARY_GREEN),
        ("2. Dialect Fine-Tuning", "Expand Whisper ASR to regional Hindi dialects (Bhojpuri, Bundelkhandi, Malvi, Chhattisgarhi) collected via Krishi Vigyan Kendras.", ACCENT_AMBER),
        ("3. Mobile Snapdragon App", "Package ONNX/QNN runtime into native Android APK for Snapdragon mobile chipsets (Snapdragon 8 Gen 3/4) for field agents.", QUALCOMM_RED)
    ]
    for i, (head, text, col) in enumerate(columns):
        left = Inches(0.8 + i * 3.98)
        col_card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0), Inches(3.76), Inches(4.5))
        col_card.fill.solid()
        col_card.fill.fore_color.rgb = SURFACE_BG
        col_card.line.color.rgb = col
        col_card.line.width = Pt(1.5)

        tb = s8.shapes.add_textbox(left + Inches(0.2), Inches(2.3), Inches(3.36), Inches(3.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = head
        p_h.font.size = Pt(18)
        p_h.font.bold = True
        p_h.font.color.rgb = col
        p_h.space_after = Pt(14)

        p_t = tf.add_paragraph()
        p_t.text = text
        p_t.font.size = Pt(14)
        p_t.font.color.rgb = TEXT_MUTED

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f"✓ Presentation saved to: {output_path}")

if __name__ == "__main__":
    out_file = Path("docs/AgriSense_Edge_Presentation.pptx")
    create_deck(out_file)
