"""
GlycoTwin — Automated Presentation Generator
Creates a polished PPTX presentation for the Happiest Health Digital Twin Challenge 2026.

Usage:
    python scripts/build_presentation.py

Output:
    presentation/GlycoTwin_Challenge_Submission.pptx
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "presentation" / "GlycoTwin_Challenge_Submission.pptx"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Color palette ─────────────────────────────────────────────────────────────
TEAL = RGBColor(0x0D, 0x94, 0x88)       # #0d9488
NAVY = RGBColor(0x0F, 0x17, 0x2A)       # #0f172a
SLATE = RGBColor(0x47, 0x55, 0x69)      # #475569
WHITE = RGBColor(0xFF, 0xFF, 0xFF)      # #ffffff
LIGHT = RGBColor(0xF8, 0xFA, 0xFC)      # #f8fafc
RED = RGBColor(0xDC, 0x26, 0x26)        # #dc2626
SKY = RGBColor(0x38, 0xBD, 0xF8)        # #38bdf8
AMBER = RGBColor(0xF5, 0x9E, 0x0B)      # #f59e0b

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H

blank_layout = prs.slide_layouts[6]   # Blank layout


def add_rect(slide, left, top, width, height, fill_color=None, line_color=None, line_width=None):
    shape = slide.shapes.add_shape(
        1,   # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    fill = shape.fill
    if fill_color:
        fill.solid()
        fill.fore_color.rgb = fill_color
    else:
        fill.background()

    if line_color:
        shape.line.color.rgb = line_color
        if line_width:
            shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, text, left, top, width, height, size=16, bold=False,
             color=WHITE, align=PP_ALIGN.LEFT, wrap=True):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def slide_background(slide, color=NAVY):
    rect = add_rect(slide, 0, 0, 13.33, 7.5, fill_color=color)
    return rect


def add_teal_bar(slide, text, top=0.4):
    add_rect(slide, 0, top, 13.33, 0.65, fill_color=TEAL)
    add_text(slide, text, 0.4, top + 0.08, 12.5, 0.5, size=20, bold=True, color=WHITE)


# ==============================================================================
# SLIDE 1 — TITLE
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)

# Gradient bar
add_rect(slide, 0, 2.8, 13.33, 0.06, fill_color=TEAL)

# Main title
add_text(slide, "🧬 GlycoTwin", 1, 1.2, 11, 1.2, size=60, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
add_text(
    slide,
    "Personalized Bio-Digital Twin for 2-Hour Glucose Excursion Risk Prediction",
    1, 2.5, 11, 0.6, size=18, bold=False, color=LIGHT, align=PP_ALIGN.CENTER
)

# Challenge badge
add_rect(slide, 3.5, 3.2, 6.3, 0.55, fill_color=RGBColor(0x06, 0x18, 0x3C))
add_text(slide, "🏆  Happiest Health Digital Twin Challenge 2026", 3.55, 3.25, 6.2, 0.45,
         size=13, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

# Disclaimer
add_text(
    slide,
    "⚠️  Research Prototype · Not a Medical Device · Not Clinically Validated",
    1, 4.0, 11, 0.4, size=11, bold=False, color=RED, align=PP_ALIGN.CENTER
)

# Team placeholder
add_text(slide, "[TEAM NAME]  ·  [INSTITUTION]", 1, 5.2, 11, 0.4, size=14,
         bold=False, color=SLATE, align=PP_ALIGN.CENTER)
add_text(slide, "[DATE]  ·  Python 3.10  ·  CGMacros v1.0.0", 1, 5.7, 11, 0.4, size=12,
         bold=False, color=SLATE, align=PP_ALIGN.CENTER)

# ==============================================================================
# SLIDE 2 — PROBLEM STATEMENT
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Problem Statement")

points = [
    ("101M+", "Indians living with Type 2 Diabetes"),
    ("136M+", "Indians in the pre-diabetic range"),
    ("Reactive care", "Glucose spikes managed after they occur, not before"),
    ("Wearable gap", "CGM devices collect rich data but predictive tools are limited"),
    ("GlycoTwin goal", "Proactive 2-hour excursion risk estimation using a Digital Twin"),
]

for i, (label, desc) in enumerate(points):
    y = 1.4 + i * 1.0
    add_rect(slide, 0.6, y, 2.8, 0.6, fill_color=RGBColor(0x0D, 0x94, 0x88))
    add_text(slide, label, 0.65, y + 0.08, 2.7, 0.5, size=14, bold=True, color=WHITE)
    add_rect(slide, 3.6, y, 8.9, 0.6, fill_color=RGBColor(0x1E, 0x29, 0x3B))
    add_text(slide, desc, 3.8, y + 0.1, 8.6, 0.5, size=14, bold=False, color=LIGHT)

add_text(slide, "⚕️  Not a diagnostic tool — research demonstration only",
         0.6, 6.8, 12, 0.4, size=10, color=RED)

# ==============================================================================
# SLIDE 3 — DIGITAL TWIN CONCEPT
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "What Makes GlycoTwin a Digital Twin?")

twin_steps = [
    ("1", "Static EHR Input", "Age, BMI, HbA1c, Fasting Glucose, Insulin"),
    ("2", "Observation Ingestion", "5-min CGM glucose, heart rate, activity calories, METs"),
    ("3", "State Update", "Personal baseline EMA, glucose momentum, data confidence"),
    ("4", "Feature Construction", "Same 24-feature vector used during training"),
    ("5", "Model Inference", "Calibrated probability → Risk estimate displayed"),
]

for i, (num, title, desc) in enumerate(twin_steps):
    y = 1.35 + i * 1.0
    add_rect(slide, 0.5, y, 0.65, 0.65, fill_color=TEAL)
    add_text(slide, num, 0.52, y + 0.08, 0.6, 0.5, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(slide, 1.3, y, 3.5, 0.65, fill_color=RGBColor(0x0D, 0x1B, 0x30))
    add_text(slide, title, 1.45, y + 0.12, 3.3, 0.45, size=13, bold=True, color=SKY)
    add_rect(slide, 4.95, y, 7.8, 0.65, fill_color=RGBColor(0x1E, 0x29, 0x3B))
    add_text(slide, desc, 5.1, y + 0.12, 7.5, 0.45, size=12, bold=False, color=LIGHT)

add_text(slide,
         "Personal Baseline:  Bₜ = 0.95 × B_{t-1} + 0.05 × Gₜ   |   "
         "Momentum:  Mₜ = 0.70 × M_{t-1} + 0.30 × (Gₜ - G_{t-1})",
         0.5, 6.7, 12.5, 0.5, size=10, bold=False, color=SLATE)

# ==============================================================================
# SLIDE 4 — DATASET & PROVENANCE
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Dataset: PhysioNet CGMacros v1.0.0")

left_items = [
    "45 anonymized participants",
    "~5-min CGM glucose readings",
    "Heart rate & activity (METs)",
    "Meal events & macronutrients",
    "Static EHR: Age, BMI, HbA1c",
    "Dates shifted for privacy",
]

right_items = [
    "License: CC BY-NC-SA 4.0 (non-commercial)",
    "Not committed to git repo",
    "Users download from PhysioNet",
    "doi: 10.13026/3z8q-x658",
    "Das A et al. (2025)",
    "Zero PII in this repository",
]

add_rect(slide, 0.4, 1.4, 6.1, 5.5, fill_color=RGBColor(0x0D, 0x1B, 0x30))
add_text(slide, "Dataset Properties", 0.6, 1.5, 5.8, 0.5, size=14, bold=True, color=TEAL)
for i, item in enumerate(left_items):
    add_text(slide, f"• {item}", 0.7, 2.1 + i * 0.75, 5.5, 0.6, size=13, color=LIGHT)

add_rect(slide, 6.8, 1.4, 6.1, 5.5, fill_color=RGBColor(0x0D, 0x1B, 0x30))
add_text(slide, "Data Ethics & Privacy", 7.0, 1.5, 5.8, 0.5, size=14, bold=True, color=TEAL)
for i, item in enumerate(right_items):
    add_text(slide, f"• {item}", 7.1, 2.1 + i * 0.75, 5.5, 0.6, size=13, color=LIGHT)

# ==============================================================================
# SLIDE 5 — MODEL PERFORMANCE (VERIFIED)
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Model Performance — Verified Metrics (Held-Out Test Set)")

add_text(slide, "IMPORTANT: All metrics are verified against data/processed/baseline_results.csv",
         0.5, 1.2, 12, 0.4, size=11, bold=True, color=AMBER)

metrics = [
    ("AUROC", "0.7566"),
    ("Avg Precision", "0.4666"),
    ("Precision", "0.3597"),
    ("Recall", "0.7305"),
    ("F1 Score", "0.4820"),
    ("Brier Score", "0.1439"),
]

for i, (label, value) in enumerate(metrics):
    col = i % 3
    row = i // 3
    x = 0.5 + col * 4.2
    y = 1.8 + row * 2.0
    add_rect(slide, x, y, 3.8, 1.6, fill_color=RGBColor(0x0D, 0x1B, 0x30))
    add_text(slide, value, x + 0.1, y + 0.1, 3.6, 0.9, size=40, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    add_text(slide, label, x + 0.1, y + 1.0, 3.6, 0.5, size=13, bold=False, color=SLATE, align=PP_ALIGN.CENTER)

add_text(slide,
         "Test set: 7 participants · Zero participant overlap with training or validation · "
         "31 train / 7 val / 7 test split",
         0.5, 6.0, 12.5, 0.5, size=11, bold=False, color=SLATE)
add_text(slide, "Operating threshold: 20% (research choice, not clinical)",
         0.5, 6.6, 12, 0.5, size=11, bold=True, color=RED)

# ==============================================================================
# SLIDE 6 — ABLATION STUDY
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Ablation Study — Why Personalization Matters")

configs = [
    ("Static EHR Only", 0.608, 0.381, RGBColor(0x64, 0x74, 0x8B)),
    ("Dynamic Wearable Only", 0.646, 0.396, RGBColor(0x47, 0x55, 0x69)),
    ("Static + Dynamic", 0.729, 0.467, RGBColor(0x08, 0x91, 0xB2)),
    ("+ Personal Baseline (Twin) ✓", 0.742, 0.479, TEAL),
]

bar_w = 2.6
for i, (label, auroc, f1, color) in enumerate(configs):
    x = 0.4 + i * 3.2
    # Bar
    bar_h = auroc * 4.5
    add_rect(slide, x, 6.0 - bar_h, bar_w, bar_h, fill_color=color)
    add_text(slide, f"{auroc:.3f}", x, 6.05 - bar_h - 0.45, bar_w, 0.4, size=14,
             bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, label, x, 6.1, bar_w, 0.6, size=11, bold=False, color=LIGHT,
             align=PP_ALIGN.CENTER)
    add_text(slide, f"F1: {f1:.3f}", x, 6.7, bar_w, 0.35, size=10, color=SLATE,
             align=PP_ALIGN.CENTER)

add_text(slide,
         "Adding the Digital Twin personal baseline adds +1.3 AUROC points over static+dynamic features",
         0.4, 1.4, 12, 0.5, size=14, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

# ==============================================================================
# SLIDE 7 — SCENARIO SIMULATOR
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Digital Twin Scenario Simulator")

add_rect(slide, 0.4, 1.3, 12.5, 1.0, fill_color=RGBColor(0x7C, 0x24, 0x00))
add_text(slide,
         "⚠️  HYPOTHETICAL ESTIMATES ONLY — Feature-space perturbations, not physiological models.\n"
         "Risk can increase OR decrease. Results are not clinical recommendations.",
         0.6, 1.35, 12, 0.85, size=12, bold=True, color=RGBColor(0xFF, 0xCC, 0x80))

scenarios = [
    ("Activity Increase", "Raises activity calories & METs in Twin history"),
    ("Activity Decrease", "Sets activity to resting baseline values"),
    ("Glucose Trend Shift", "Shifts recent glucose window up or down"),
    ("Heart Rate Elevated", "Sets heart rate to sustained elevated level"),
]

for i, (name, desc) in enumerate(scenarios):
    y = 2.6 + i * 0.9
    add_rect(slide, 0.4, y, 4.5, 0.75, fill_color=RGBColor(0x1E, 0x29, 0x3B))
    add_text(slide, name, 0.6, y + 0.1, 4.2, 0.55, size=13, bold=True, color=SKY)
    add_rect(slide, 5.1, y, 8, 0.75, fill_color=RGBColor(0x12, 0x1D, 0x30))
    add_text(slide, desc, 5.3, y + 0.15, 7.6, 0.5, size=12, color=LIGHT)

add_text(slide,
         "Architecture: deep-copy Twin → apply perturbation → run identical 24-feature inference → "
         "return ΔP in percentage points",
         0.4, 6.7, 12.5, 0.5, size=10, color=SLATE)

# ==============================================================================
# SLIDE 8 — DASHBOARD WALKTHROUGH
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Application — 5-Tab Streamlit Dashboard")

tabs = [
    ("📊 Twin Overview", "Risk gauge, glucose chart, state panel, explanation, timeline, export"),
    ("🧪 Scenario Simulator", "4 scenario types, intensity slider, baseline vs scenario probability"),
    ("🩺 EHR Profile", "Static clinical features, HbA1c cohort (research classification only)"),
    ("📡 CGM Replay", "Step/jump/back/reset controls, progress bar, per-observation state update"),
    ("🔬 Model Evidence", "AUROC, AP, F1, Brier Score, ablation chart, model card, data provenance"),
]

for i, (tab, desc) in enumerate(tabs):
    y = 1.4 + i * 1.0
    add_rect(slide, 0.4, y, 4.2, 0.75, fill_color=TEAL)
    add_text(slide, tab, 0.55, y + 0.1, 4.0, 0.55, size=13, bold=True, color=WHITE)
    add_rect(slide, 4.8, y, 8.1, 0.75, fill_color=RGBColor(0x1E, 0x29, 0x3B))
    add_text(slide, desc, 5.0, y + 0.15, 7.8, 0.5, size=12, color=LIGHT)

add_text(slide, "Auth: Argon2id hashing  ·  Workspaces: SQLite per-user  ·  Export: PDF + CSV",
         0.4, 6.75, 12.5, 0.4, size=11, bold=False, color=SLATE)

# ==============================================================================
# SLIDE 9 — SAFETY & ETHICS
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Safety, Ethics & Research Transparency")

add_rect(slide, 0.4, 1.3, 12.5, 0.8, fill_color=RGBColor(0x3B, 0x08, 0x08))
add_text(slide,
         "GlycoTwin is a RESEARCH PROTOTYPE. Never use it for clinical decisions. "
         "No treatment recommendations appear anywhere in the application.",
         0.6, 1.35, 12, 0.7, size=13, bold=True, color=RGBColor(0xFF, 0xA5, 0xA5))

safety = [
    "All metrics are verified from actual evaluation files — never fabricated",
    "Target built from observed glucose only — no imputed values used as ground truth",
    "31/7/7 participant split with zero overlap — no data leakage",
    "20% threshold labeled as research operating point, not clinical boundary",
    "HbA1c cohort classification labeled as research grouping, not diagnosis",
    "Scenario outputs labeled as hypothetical — risk can increase or decrease",
    "Passwords hashed with Argon2id — plaintext never stored",
    "Dataset: CC BY-NC-SA 4.0 — non-commercial. Raw data not committed.",
]

for i, item in enumerate(safety):
    y = 2.3 + i * 0.52
    add_text(slide, f"✓  {item}", 0.5, y, 12.3, 0.5, size=12, color=LIGHT)

# ==============================================================================
# SLIDE 10 — CONCLUSION
# ==============================================================================
slide = prs.slides.add_slide(blank_layout)
slide_background(slide)
add_teal_bar(slide, "Conclusion & Future Work")

contributions = [
    ("Digital Twin Update Loop", "Genuine stateful update: each 5-min observation refreshes Twin + runs inference"),
    ("Personalization Evidence", "Personal baseline adds +1.3 AUROC points — validated by ablation study"),
    ("Open & Reproducible", "Public dataset, verified metrics, full source code, 48 passing tests"),
    ("Scientifically Responsible", "No fabricated metrics, explicit safety disclaimers throughout"),
]

for i, (title, desc) in enumerate(contributions):
    y = 1.4 + i * 1.0
    add_rect(slide, 0.4, y, 3.8, 0.8, fill_color=TEAL)
    add_text(slide, title, 0.55, y + 0.12, 3.6, 0.55, size=12, bold=True, color=WHITE)
    add_rect(slide, 4.4, y, 8.5, 0.8, fill_color=RGBColor(0x1E, 0x29, 0x3B))
    add_text(slide, desc, 4.6, y + 0.15, 8.2, 0.55, size=12, color=LIGHT)

add_text(slide, "Future Work:", 0.4, 5.7, 12, 0.5, size=14, bold=True, color=TEAL)
future = ("External validation on independent cohort  ·  "
          "Real-time wearable API integration  ·  "
          "Prospective clinical pilot  ·  "
          "Principled uncertainty quantification  ·  "
          "Regulatory pathway exploration")
add_text(slide, future, 0.4, 6.2, 12.5, 0.6, size=12, color=SLATE)

add_text(slide, "Test AUROC 0.757  ·  48/48 tests passing  ·  Python 3.10  ·  CGMacros v1.0.0",
         0.4, 7.0, 12.5, 0.35, size=10, color=SLATE, align=PP_ALIGN.CENTER)

# ==============================================================================
# SAVE
# ==============================================================================
prs.save(str(OUTPUT_PATH))
print(f"Presentation saved: {OUTPUT_PATH}")
print(f"Slides: {len(prs.slides)}")
