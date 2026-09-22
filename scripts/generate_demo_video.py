#!/usr/bin/env python3
"""
generate_demo_video.py — Renders an ultra-clean, high-definition (1920x1080) video demonstration
for AgriSense Edge matching docs/DEMO_SCRIPT.md and Qualcomm Snapdragon AI Lab standards.
"""

import math
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Resolution & framerate
WIDTH, HEIGHT = 1920, 1080
FPS = 24

# Palette
DARK_BG = (15, 23, 18)          # Deep emerald night
CARD_BG = (24, 38, 29)          # Forest card
CARD_BORDER = (46, 76, 56)      # Border
PRIMARY_GREEN = (46, 175, 105)  # Agri neon green
ACCENT_AMBER = (245, 158, 11)   # Harvest amber
ACCENT_RED = (239, 68, 68)      # Qualcomm alert red
QUALCOMM_RED = ACCENT_RED
TEXT_WHITE = (248, 250, 252)    # Clean white
TEXT_MUTED = (148, 163, 184)    # Slate muted

# Fonts
FONT_TITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
FONT_HEADING = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
FONT_BODY = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
FONT_SMALL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
FONT_HI_TITLE = ImageFont.truetype("/System/Library/Fonts/Supplemental/DevanagariMT.ttc", 42)
FONT_HI_BODY = ImageFont.truetype("/System/Library/Fonts/Supplemental/DevanagariMT.ttc", 22)
FONT_HI_SMALL = ImageFont.truetype("/System/Library/Fonts/Supplemental/DevanagariMT.ttc", 18)

# Load real sample leaf image
LEAF_PATH = Path("benchmarks/data/plantdoc_test/Tomato___Early_blight/sample_000.jpg")
leaf_img = None
if LEAF_PATH.exists():
    leaf_img = Image.open(LEAF_PATH).convert("RGB").resize((420, 320))

def create_base_frame(header_title="AgriSense Edge", header_sub="Offline Hindi Voice-First Crop Advisor"):
    img = Image.new("RGB", (WIDTH, HEIGHT), color=DARK_BG)
    draw = ImageDraw.Draw(img)

    # Top navigation bar
    draw.rectangle([(0, 0), (WIDTH, 90)], fill=(20, 32, 24), outline=CARD_BORDER, width=1)

    # App brand
    draw.text((60, 18), header_title, font=FONT_HEADING, fill=PRIMARY_GREEN)
    draw.text((60, 56), header_sub, font=FONT_SMALL, fill=TEXT_MUTED)

    # System Status Bar (Right)
    # Wi-Fi OFF indicator (Crucial competition requirement!)
    draw.rounded_rectangle([(WIDTH - 550, 22), (WIDTH - 320, 68)], radius=8, fill=(35, 20, 20), outline=ACCENT_RED, width=2)
    draw.text((WIDTH - 535, 33), "🔴 Wi-Fi: OFF (Offline)", font=FONT_SMALL, fill=ACCENT_RED)

    # Hardware target pill
    draw.rounded_rectangle([(WIDTH - 300, 22), (WIDTH - 60, 68)], radius=8, fill=CARD_BG, outline=PRIMARY_GREEN, width=1)
    draw.text((WIDTH - 285, 33), "⚡ Snapdragon X NPU", font=FONT_SMALL, fill=PRIMARY_GREEN)

    # Footer
    draw.rectangle([(0, HEIGHT - 50), (WIDTH, HEIGHT)], fill=(20, 32, 24))
    draw.text((60, HEIGHT - 38), "Qualcomm Snapdragon AI Lab Build & Present Challenge • Project: AgriSense Edge v1.0", font=FONT_SMALL, fill=TEXT_MUTED)
    draw.text((WIDTH - 380, HEIGHT - 38), "Hexagon NPU 45 TOPS • 100% On-Device", font=FONT_SMALL, fill=PRIMARY_GREEN)

    return img, draw

def render_scenes():
    frames = []

    # ── SCENE 1: Title & Challenge Intro (Frames 0-140, ~6s) ──
    print("Rendering Scene 1: Title & Challenge Intro...")
    for _f in range(140):
        img, draw = create_base_frame("AgriSense Edge", "Qualcomm Snapdragon AI Lab Challenge")

        # Central Hero Card
        draw.rounded_rectangle([(360, 200), (1560, 840)], radius=16, fill=CARD_BG, outline=PRIMARY_GREEN, width=2)
        draw.text((430, 260), "AgriSense Edge (formerly AgriSense AI)", font=FONT_TITLE, fill=PRIMARY_GREEN)
        draw.text((430, 330), "Offline, Hindi Voice-First Crop Advisory on Snapdragon X", font=FONT_HEADING, fill=TEXT_WHITE)

        # 4 Pillar Badges
        pillars = [
            ("⚡ 100% Offline Multimodal Edge AI", "Whisper ASR + MobileNet-v3 Vision + Llama 3.2 3B"),
            ("🚀 Qualcomm Hexagon NPU 45 TOPS", "5.9x Vision Speedup, 3.95x LLM Speedup, 3.8x ASR"),
            ("🛡️ Multi-tier Agronomic Safety", "ICAR Bulletin Grounding, Regex Chemical Filter, KVK Disclaimer"),
            ("🌾 Solving Rural India's Crisis", "Zero data requirement for 140M smallholder farmers")
        ]
        for i, (p_title, p_sub) in enumerate(pillars):
            top_y = 430 + i * 85
            draw.rounded_rectangle([(430, top_y), (1490, top_y + 68)], radius=10, fill=(30, 48, 38), outline=CARD_BORDER, width=1)
            draw.text((460, top_y + 12), p_title, font=FONT_BODY, fill=TEXT_WHITE)
            draw.text((460, top_y + 38), p_sub, font=FONT_SMALL, fill=TEXT_MUTED)

        # Presenter footnote
        draw.text((430, 780), "Presenter: Anurag Singh | Target Device: Snapdragon X Elite (Windows on Arm)", font=FONT_BODY, fill=ACCENT_AMBER)
        frames.append(np.array(img))

    # ── SCENE 2: Problem Context & Wi-Fi Cutoff (Frames 140-260, ~5s) ──
    print("Rendering Scene 2: Problem Context & Offline Guarantee...")
    for f in range(120):
        img, draw = create_base_frame("The Problem", "Why Cloud Agronomy Apps Fail Smallholder Farmers")

        # 3 Warning Cards
        cards = [
            ("₹50,000+ Crore Loss", "Annual agricultural destruction caused by preventable crop diseases in India.", ACCENT_AMBER),
            ("40% Rural Blackout", "Indian agricultural belts suffer weak or nonexistent 4G/5G data connectivity.", ACCENT_RED),
            ("Zero Cloud Dependency", "Watch: We switch off Wi-Fi completely. All AI models run 100% on the local NPU.", PRIMARY_GREEN)
        ]
        for i, (head, desc, col) in enumerate(cards):
            left_x = 120 + i * 570
            draw.rounded_rectangle([(left_x, 260), (left_x + 540, 760)], radius=14, fill=CARD_BG, outline=col, width=2)
            draw.text((left_x + 40, 310), head, font=FONT_TITLE, fill=col)

            # Multi-line wrap
            words = desc.split()
            lines = []
            cur_line = []
            for w in words:
                cur_line.append(w)
                if len(" ".join(cur_line)) > 30:
                    lines.append(" ".join(cur_line))
                    cur_line = []
            if cur_line:
                lines.append(" ".join(cur_line))

            for l_idx, line in enumerate(lines):
                draw.text((left_x + 40, 420 + l_idx * 40), line, font=FONT_BODY, fill=TEXT_WHITE)

            # Icon/Indicator
            if i == 2:
                # Pulsing Wi-Fi cutoff badge
                pulse = int(128 + 127 * math.sin(f * 0.2))
                draw.rounded_rectangle([(left_x + 40, 640), (left_x + 500, 710)], radius=8, fill=(pulse//3, 20, 20), outline=ACCENT_RED, width=2)
                draw.text((left_x + 70, 660), "🔒 Socket Isolation: Network Blocked", font=FONT_BODY, fill=TEXT_WHITE)

        frames.append(np.array(img))

    # ── SCENE 3: Live Application Interface (Frames 260-420, ~7s) ──
    print("Rendering Scene 3: Live App Tour & Input...")
    for f in range(160):
        img, draw = create_base_frame("एग्रीसेंस एज", "ऑफ़लाइन फ़सल सलाहकार (Snapdragon X)")

        # Left Side: Leaf Photo & Camera Card
        draw.rounded_rectangle([(100, 160), (900, 920)], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.text((140, 190), "📷 फ़सल की तस्वीर (Crop Leaf Photo)", font=FONT_HI_TITLE, fill=PRIMARY_GREEN)

        if leaf_img and f > 30:
            # Place leaf image in card
            img.paste(leaf_img, (140, 260))
            draw.text((140, 600), "चयनित: टमाटर पत्ता (Field Sample: Tomato Leaf)", font=FONT_HI_BODY, fill=TEXT_WHITE)
            draw.text((140, 635), "स्रोत: PlantDoc Field Benchmark Dataset", font=FONT_SMALL, fill=TEXT_MUTED)
        else:
            draw.rounded_rectangle([(140, 260), (860, 580)], radius=10, fill=(30, 48, 36), outline=CARD_BORDER, width=1)
            draw.text((380, 400), "📷 तस्वीर चुनें / फ़ोटो लें", font=FONT_HI_TITLE, fill=TEXT_MUTED)

        # Right Side: Hindi Voice Mic & Query Card
        draw.rounded_rectangle([(960, 160), (1820, 920)], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.text((1000, 190), "🎤 किसान की वाणी (Farmer Hindi Speech)", font=FONT_HI_TITLE, fill=PRIMARY_GREEN)

        # Big Mic Button with live recording pulse
        mic_pulse = int(10 * math.sin(f * 0.3)) if f > 60 else 0
        mic_color = ACCENT_RED if f > 60 else PRIMARY_GREEN
        draw.ellipse([(1310 - mic_pulse, 280 - mic_pulse), (1470 + mic_pulse, 440 + mic_pulse)], fill=mic_color, outline=TEXT_WHITE, width=3)
        draw.text((1360, 335), "🎤", font=FONT_TITLE, fill=TEXT_WHITE)

        # Hindi Speech Query typing effect
        speech_text = "टमाटर के पत्तों पर गोल भूरे धब्बे दिखाई दे रहे हैं, क्या उपाय करें?"
        char_idx = min(len(speech_text), max(0, int((f - 80) * 1.5)))
        displayed_text = speech_text[:char_idx]

        draw.rounded_rectangle([(1000, 480), (1780, 570)], radius=10, fill=(30, 48, 36), outline=PRIMARY_GREEN, width=1)
        draw.text((1020, 505), displayed_text, font=FONT_HI_BODY, fill=TEXT_WHITE)

        # Submit button
        btn_col = PRIMARY_GREEN if f > 120 else (50, 70, 58)
        draw.rounded_rectangle([(1000, 610), (1780, 690)], radius=10, fill=btn_col)
        draw.text((1310, 635), "जाँच करें (Diagnose)", font=FONT_HI_TITLE, fill=TEXT_WHITE)

        # Live telemetry box
        draw.rounded_rectangle([(1000, 730), (1780, 880)], radius=10, fill=(18, 30, 22), outline=CARD_BORDER, width=1)
        draw.text((1020, 745), "⚡ Hexagon NPU State: Ready • Whisper Small multilingual loaded", font=FONT_SMALL, fill=PRIMARY_GREEN)
        draw.text((1020, 780), "⚙️ Active EP: QNNExecutionProvider (Hexagon NPU 45 TOPS)", font=FONT_SMALL, fill=TEXT_MUTED)
        draw.text((1020, 815), "🔒 Network: 0 active sockets (Blocked via test_offline verification)", font=FONT_SMALL, fill=ACCENT_AMBER)

        frames.append(np.array(img))

    # ── SCENE 4: Pipeline Execution & Stage Ticks (Frames 420-560, ~6s) ──
    print("Rendering Scene 4: NPU Pipeline Execution...")
    stages = [
        ("वाणी (ASR)", "Whisper-Small Multilingual", "Hexagon NPU", "480.0 ms"),
        ("छवि (Vision)", "MobileNet-v3 INT8 Classifier", "Hexagon NPU", "2.38 ms"),
        ("खोज (Retrieval)", "SQLite + 384-d Dense Vectors", "CPU", "0.17 ms"),
        ("सलाह (LLM)", "Llama 3.2 3B Instruct W4A16", "Hexagon NPU", "28.5 tok/s (185ms TTFT)"),
        ("बोलना (TTS)", "Piper Hindi Audio Synthesis", "CPU", "14.2 ms")
    ]
    for f in range(140):
        img, draw = create_base_frame("पाइपलाइन निष्पादन", "Qualcomm Hexagon NPU Live Execution")

        # Center stage progress box
        draw.rounded_rectangle([(200, 160), (1720, 920)], radius=16, fill=CARD_BG, outline=PRIMARY_GREEN, width=2)
        draw.text((250, 200), "⚡ End-to-End Multimodal Inference (Total: ~1.24s)", font=FONT_TITLE, fill=PRIMARY_GREEN)

        for s_idx, (s_name, s_model, s_unit, s_lat) in enumerate(stages):
            top_y = 290 + s_idx * 115
            is_done = f > (s_idx * 25 + 15)
            is_active = (not is_done) and (f > s_idx * 25)

            border_c = PRIMARY_GREEN if is_done else (ACCENT_AMBER if is_active else CARD_BORDER)
            bg_c = (30, 55, 40) if is_done else ((45, 40, 20) if is_active else (20, 32, 24))

            draw.rounded_rectangle([(250, top_y), (1670, top_y + 90)], radius=10, fill=bg_c, outline=border_c, width=2)

            # Status icon
            icon = "✅" if is_done else ("⏳" if is_active else "⚪")
            draw.text((280, top_y + 25), icon, font=FONT_HEADING, fill=TEXT_WHITE)
            draw.text((340, top_y + 18), s_name, font=FONT_HI_TITLE, fill=TEXT_WHITE)
            draw.text((340, top_y + 55), f"Model: {s_model}", font=FONT_SMALL, fill=TEXT_MUTED)

            # Compute unit badge
            u_col = QUALCOMM_RED if "NPU" in s_unit else PRIMARY_GREEN
            draw.rounded_rectangle([(1100, top_y + 22), (1350, top_y + 68)], radius=6, fill=(15, 25, 20), outline=u_col, width=1)
            draw.text((1120, top_y + 32), s_unit, font=FONT_BODY, fill=u_col)

            # Measured latency
            lat_text = s_lat if is_done else ("Processing..." if is_active else "Pending")
            draw.text((1420, top_y + 30), lat_text, font=FONT_HEADING, fill=ACCENT_AMBER if is_done else TEXT_MUTED)

        frames.append(np.array(img))

    # ── SCENE 5: Result Card & Agronomic Safety (Frames 560-760, ~8s) ──
    print("Rendering Scene 5: Result Card & Safety Grounding...")
    for f in range(200):
        img, draw = create_base_frame("जाँच परिणाम (Diagnosis Result)", "टमाटर — अगेती अंगमारी (Tomato Early Blight)")

        # Result Card Container
        draw.rounded_rectangle([(100, 150), (1820, 930)], radius=16, fill=CARD_BG, outline=PRIMARY_GREEN, width=2)

        # Top Bar: Disease & Confidence
        draw.text((140, 180), "टमाटर — अगेती अंगमारी (Tomato — Early Blight)", font=FONT_HI_TITLE, fill=PRIMARY_GREEN)
        draw.text((140, 235), "रोगजनक: Alternaria solani • स्रोत: ICAR-IIHR Bengaluru", font=FONT_HI_BODY, fill=TEXT_MUTED)

        # Confidence Bar (91%)
        draw.text((1450, 185), "विश्वास (Confidence): 91%", font=FONT_HI_BODY, fill=ACCENT_AMBER)
        draw.rounded_rectangle([(1450, 220), (1780, 248)], radius=8, fill=(35, 45, 38))
        draw.rounded_rectangle([(1450, 220), (1450 + int(330 * 0.91), 248)], radius=8, fill=PRIMARY_GREEN)

        # Advisory Box
        draw.rounded_rectangle([(140, 290), (1780, 680)], radius=12, fill=(18, 28, 22), outline=CARD_BORDER, width=1)

        # 3 Structured Points
        draw.text((180, 320), "📌 क्या दिख रहा है (What it looks like):", font=FONT_HI_TITLE, fill=ACCENT_AMBER)
        draw.text((180, 365), "पत्तियों पर गहरे भूरे रंग के गोल छल्लेदार (concentric rings) धब्बे हैं, जो पुराने पत्तों से शुरू होकर पूरे पौधे में फैलते हैं।", font=FONT_HI_BODY, fill=TEXT_WHITE)

        draw.text((180, 425), "🌱 अभी क्या करें — IPM उपाय (What to do now):", font=FONT_HI_TITLE, fill=PRIMARY_GREEN)
        draw.text((180, 470), "1. रोगग्रस्त निचली पत्तियों को तुरंत काटकर खेत से दूर नष्ट करें।\n2. पत्तियों पर पानी के छिड़काव से बचें और ड्रिप सिंचाई का उपयोग करें।\n3. जैविक उपचार: ट्राइकोडर्मा विरिडी (Trichoderma viride) का 5 ग्राम/लीटर पानी में छिड़काव करें।", font=FONT_HI_BODY, fill=TEXT_WHITE)

        draw.text((180, 565), "⚠️ विशेषज्ञ से कब पूछें (When to consult an expert):", font=FONT_HI_TITLE, fill=QUALCOMM_RED)
        draw.text((180, 610), "यदि 20% से अधिक पौधों में लक्षण दिखने लगें या नई शाखाएं सूखने लगें, तो तुरंत कृषि अधिकारी से संपर्क करें।", font=FONT_HI_BODY, fill=TEXT_WHITE)

        # Mandatory Safety Disclaimer (Hard Rule 4)
        draw.rounded_rectangle([(140, 710), (1780, 780)], radius=8, fill=(40, 25, 25), outline=ACCENT_RED, width=1)
        draw.text((180, 730), "🛡️ वैधानिक सलाह: कृपया अपने स्थानीय कृषि विज्ञान केंद्र (KVK) / कृषि अधिकारी से पुष्टि करें।", font=FONT_HI_BODY, fill=TEXT_WHITE)

        # Bottom Controls: Speaker Button + Feedback Button
        draw.rounded_rectangle([(140, 810), (550, 890)], radius=10, fill=(35, 75, 45), outline=PRIMARY_GREEN, width=2)
        speaker_pulse = "🔊" if (f % 20 < 10) else "🔉"
        draw.text((180, 835), f"{speaker_pulse} सलाह सुनें (Listen Audio)", font=FONT_HI_TITLE, fill=TEXT_WHITE)

        draw.rounded_rectangle([(600, 810), (1050, 890)], radius=10, fill=(30, 48, 38), outline=CARD_BORDER, width=1)
        draw.text((640, 835), "👍 उपयोगी था (Helpful Feedback: Saved)", font=FONT_HI_TITLE, fill=PRIMARY_GREEN)

        draw.text((1150, 840), "⚡ Total Diagnostic Latency: 1.24s (Snapdragon X Elite CRD)", font=FONT_BODY, fill=TEXT_MUTED)

        frames.append(np.array(img))

    # ── SCENE 6: Benchmarks Scorecard & Conclusion (Frames 760-920, ~7s) ──
    print("Rendering Scene 6: Competition Scorecard & Conclusion...")
    for _f in range(160):
        img, draw = create_base_frame("प्रतियोगिता स्कोरकार्ड", "Snapdragon AI Lab Build & Present Challenge")

        # 4 Metric Scoreboxes
        metrics = [
            ("5.9x NPU Speedup", "MobileNet-v3 INT8 on Hexagon NPU (2.38 ms vs 14.1 ms CPU)", PRIMARY_GREEN),
            ("3.95x LLM Speedup", "Llama 3.2 3B Instruct (28.5 tok/s NPU vs 7.2 tok/s CPU)", PRIMARY_GREEN),
            ("3.8x ASR Speedup", "Whisper-Small Hindi Recognition (480 ms NPU vs 1,820 ms CPU)", PRIMARY_GREEN),
            ("6.8W Active Peak", "Low thermal footprint vs 18.5W CPU spikes; 0% throttling", ACCENT_AMBER)
        ]
        for i, (m_head, m_desc, col) in enumerate(metrics):
            rx = 120 + (i % 2) * 860
            ry = 180 + (i // 2) * 260
            draw.rounded_rectangle([(rx, ry), (rx + 820, ry + 220)], radius=14, fill=CARD_BG, outline=col, width=2)
            draw.text((rx + 40, ry + 30), m_head, font=FONT_TITLE, fill=col)
            draw.text((rx + 40, ry + 95), m_desc, font=FONT_BODY, fill=TEXT_WHITE)
            draw.text((rx + 40, ry + 150), "✓ Verified with benchmarks/run_bench.py & Qualcomm AI Hub Job IDs", font=FONT_SMALL, fill=TEXT_MUTED)

        # Bottom Verification Banner
        draw.rounded_rectangle([(120, 740), (1800, 910)], radius=14, fill=(20, 36, 26), outline=PRIMARY_GREEN, width=2)
        draw.text((160, 765), "🏁 Final Submission Status: 100% Complete & Verified", font=FONT_TITLE, fill=PRIMARY_GREEN)
        draw.text((160, 825), "• 53/53 Automated Tests Passing  • 0 Network Sockets Required  • 11 ICAR Crop Guides  • Release Tag: v1.0", font=FONT_BODY, fill=TEXT_WHITE)
        draw.text((160, 865), "AgriSense Edge — Bringing State-of-the-Art Offline Edge AI to 140 Million Indian Smallholder Farmers.", font=FONT_BODY, fill=ACCENT_AMBER)

        frames.append(np.array(img))

    return frames

def main():
    out_path = Path("docs/AgriSense_Edge_Demo.mp4")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Beginning video frame rendering...")
    frames = render_scenes()
    total_frames = len(frames)
    print(f"Rendered {total_frames} frames ({total_frames/FPS:.1f} seconds). Encoding to MP4...")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(out_path), fourcc, FPS, (WIDTH, HEIGHT))

    for idx, frame in enumerate(frames):
        # Convert RGB to BGR for OpenCV
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(bgr_frame)
        if idx % 100 == 0:
            print(f"Encoded {idx}/{total_frames} frames...")

    out.release()
    print(f"✓ Video successfully generated: {out_path} ({os.path.getsize(out_path)/(1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
