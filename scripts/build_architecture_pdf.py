"""
scripts/build_architecture_pdf.py
Generates an architecture diagram PDF for GlycoTwin using reportlab.

Run from project root:
    python scripts/build_architecture_pdf.py

Output: docs/GlycoTwin_Architecture.pdf
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_PATH = PROJECT_ROOT / "docs" / "GlycoTwin_Architecture.pdf"

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER

W, H = landscape(A4)  # 297 x 210 mm -> 841.9 x 595.3 pts

# ── Color palette ──────────────────────────────────────────────────────────────
DARK_BG   = colors.HexColor("#0d1117")
PANEL_BG  = colors.HexColor("#161b22")
TEAL      = colors.HexColor("#00bfa5")
BLUE      = colors.HexColor("#1565c0")
PURPLE    = colors.HexColor("#6a0dad")
AMBER     = colors.HexColor("#f59e0b")
RED       = colors.HexColor("#e53935")
GREEN     = colors.HexColor("#2e7d32")
WHITE     = colors.HexColor("#e6edf3")
GRAY      = colors.HexColor("#8b949e")
BORDER    = colors.HexColor("#30363d")

def box(c, x, y, w, h, fill_color, border_color=BORDER, radius=6):
    c.setFillColor(fill_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(1.2)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

def label(c, text, x, y, w, size=8, color=WHITE, bold=False):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawCentredString(x + w / 2, y, text)

def arrow(c, x1, y1, x2, y2, color=GRAY):
    import math
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.5)
    c.line(x1, y1, x2, y2)
    # arrowhead as filled triangle
    angle = math.atan2(y2 - y1, x2 - x1)
    sz = 6
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - sz * math.cos(angle - 0.4), y2 - sz * math.sin(angle - 0.4))
    p.lineTo(x2 - sz * math.cos(angle + 0.4), y2 - sz * math.sin(angle + 0.4))
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def build_pdf():
    c = canvas.Canvas(str(OUTPUT_PATH), pagesize=landscape(A4))

    # ── Background ─────────────────────────────────────────────────────────────
    c.setFillColor(DARK_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Title ──────────────────────────────────────────────────────────────────
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, H - 30, "GlycoTwin — System Architecture")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, H - 46,
        "Research Prototype | Happiest Health Digital Twin Challenge 2026 | "
        "Dataset: PhysioNet CGMacros v1.0.0 (CC BY-NC-SA 4.0)")

    TOP = H - 65
    BOX_H = 52
    SMALL_H = 34

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 1:  Static EHR   |   Dynamic CGM/Wearable
    # ─────────────────────────────────────────────────────────────────────────
    # Static EHR box
    box(c, 20, TOP - BOX_H, 175, BOX_H, PANEL_BG, BLUE)
    label(c, "STATIC EHR INPUT", 20, TOP - 14, 175, 8, BLUE, True)
    label(c, "bio.csv — 45 participants", 20, TOP - 26, 175, 7.5, GRAY)
    label(c, "Age | BMI | HbA1c | Fasting Glucose | Insulin", 20, TOP - 38, 175, 7, WHITE)
    label(c, "CC BY-NC-SA 4.0 — PhysioNet CGMacros v1.0.0", 20, TOP - 50, 175, 6.5, GRAY)

    # Dynamic wearable box
    box(c, 205, TOP - BOX_H, 195, BOX_H, PANEL_BG, TEAL)
    label(c, "DYNAMIC WEARABLE INPUT", 205, TOP - 14, 195, 8, TEAL, True)
    label(c, "CGMacros-0XX.csv — 5-min intervals", 205, TOP - 26, 195, 7.5, GRAY)
    label(c, "CGM Glucose | Heart Rate | Activity Cal | METs", 205, TOP - 38, 195, 7, WHITE)
    label(c, "Approx. 10 days per participant", 205, TOP - 50, 195, 6.5, GRAY)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 1 RIGHT:  Streamlit Dashboard
    # ─────────────────────────────────────────────────────────────────────────
    box(c, 620, TOP - BOX_H, 205, BOX_H, PANEL_BG, PURPLE)
    label(c, "STREAMLIT DASHBOARD", 620, TOP - 14, 205, 8, PURPLE, True)
    label(c, "app/dashboard.py", 620, TOP - 26, 205, 7.5, GRAY)
    label(c, "Twin Overview | Scenario Sim | EHR Profile", 620, TOP - 38, 205, 7, WHITE)
    label(c, "CGM Replay | Model Evidence | Auth & Export", 620, TOP - 50, 205, 7, WHITE)

    # Arrows from inputs downward
    mid1 = 20 + 175 / 2
    mid2 = 205 + 195 / 2
    arrow(c, mid1, TOP - BOX_H, mid1, TOP - BOX_H - 18)
    arrow(c, mid2, TOP - BOX_H, mid2, TOP - BOX_H - 18)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 2:  Data cleaning / preprocessing
    # ─────────────────────────────────────────────────────────────────────────
    ROW2 = TOP - BOX_H - 18
    box(c, 20, ROW2 - SMALL_H, 380, SMALL_H, PANEL_BG, AMBER)
    label(c, "DATA CLEANING & FEATURE ENGINEERING", 20, ROW2 - 14, 380, 8, AMBER, True)
    label(c, "load_cgmacros.py | clean_cgmacros.py | build_features.py", 20, ROW2 - 26, 380, 7.5, GRAY)
    label(c, "Resampling to 5-min | NaN→0 imputation | Participant-level train/val/test split (31/7/7)", 20, ROW2 - 38, 380, 7, WHITE)

    arrow(c, 20 + 380 / 2, ROW2 - SMALL_H, 20 + 380 / 2, ROW2 - SMALL_H - 18)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 3:  Digital Twin State Engine (left)  +  Model Training (right)
    # ─────────────────────────────────────────────────────────────────────────
    ROW3 = ROW2 - SMALL_H - 18
    TWIN_W = 240
    MODEL_W = 200

    # Twin State
    box(c, 20, ROW3 - 72, TWIN_W, 72, PANEL_BG, TEAL)
    label(c, "DIGITAL TWIN STATE ENGINE", 20, ROW3 - 14, TWIN_W, 8, TEAL, True)
    label(c, "src/twin/state.py | updater.py", 20, ROW3 - 26, TWIN_W, 7.5, GRAY)
    label(c, "Personal Baseline: B_t = 0.95*B_{t-1} + 0.05*G_t", 20, ROW3 - 38, TWIN_W, 7, WHITE)
    label(c, "Glucose Momentum | Metabolic State", 20, ROW3 - 50, TWIN_W, 7, WHITE)
    label(c, "Cardiovascular State | Data Confidence", 20, ROW3 - 62, TWIN_W, 7, WHITE)
    label(c, "Updated each 5-min observation", 20, ROW3 - 74, TWIN_W, 6.5, GRAY)

    # Model training (offline, dashed border)
    box(c, 270, ROW3 - 72, MODEL_W, 72, PANEL_BG, GRAY, radius=4)
    label(c, "MODEL TRAINING (OFFLINE)", 270, ROW3 - 14, MODEL_W, 8, AMBER, True)
    label(c, "src/models/train_baseline.py", 270, ROW3 - 26, MODEL_W, 7.5, GRAY)
    label(c, "Calibrated Logistic Regression", 270, ROW3 - 38, MODEL_W, 7, WHITE)
    label(c, "Train set only (31 participants)", 270, ROW3 - 50, MODEL_W, 7, WHITE)
    label(c, "Platt scaling on val set (7 participants)", 270, ROW3 - 62, MODEL_W, 7, WHITE)
    label(c, "[Offline — never runs during dashboard use]", 270, ROW3 - 74, MODEL_W, 6.5, GRAY)

    arrow(c, 20 + TWIN_W / 2, ROW3 - 72, 20 + TWIN_W / 2, ROW3 - 72 - 18)
    arrow(c, 270 + MODEL_W / 2, ROW3 - 72, 270 + MODEL_W / 2, ROW3 - 72 - 18)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 4:  24-feature builder
    # ─────────────────────────────────────────────────────────────────────────
    ROW4 = ROW3 - 72 - 18
    FEAT_W = 470
    box(c, 20, ROW4 - SMALL_H, FEAT_W, SMALL_H, PANEL_BG, BLUE)
    label(c, "24-FEATURE VECTOR BUILDER  (src/twin/feature_builder.py)", 20, ROW4 - 14, FEAT_W, 8, BLUE, True)
    label(c, "Glucose stats (7) | Heart rate stats (3) | Activity stats (4) | METs stats (3) | Static clinical (5) | Personal baseline (2)", 20, ROW4 - 26, FEAT_W, 7, WHITE)
    label(c, "Feature ORDER identical in training and inference — verified by test_feature_contract.py", 20, ROW4 - 38, FEAT_W, 7, GRAY)

    arrow(c, 20 + FEAT_W / 2, ROW4 - SMALL_H, 20 + FEAT_W / 2, ROW4 - SMALL_H - 18)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 5:  Prediction + Scenario (side by side)
    # ─────────────────────────────────────────────────────────────────────────
    ROW5 = ROW4 - SMALL_H - 18
    PRED_W = 230
    SCEN_W = 200

    box(c, 20, ROW5 - 68, PRED_W, 68, PANEL_BG, GREEN)
    label(c, "RISK PREDICTION", 20, ROW5 - 14, PRED_W, 8, GREEN, True)
    label(c, "src/twin/predictor.py", 20, ROW5 - 26, PRED_W, 7.5, GRAY)
    label(c, "models/glycotwin_logistic_calibrated.pkl", 20, ROW5 - 38, PRED_W, 7, WHITE)
    label(c, "P(glucose rise >= 30 mg/dL in 120 min)", 20, ROW5 - 50, PRED_W, 7, WHITE)
    label(c, "Research threshold: 0.20 (not clinical)", 20, ROW5 - 62, PRED_W, 7, AMBER)

    box(c, 260, ROW5 - 68, SCEN_W, 68, PANEL_BG, AMBER)
    label(c, "SCENARIO SIMULATOR", 260, ROW5 - 14, SCEN_W, 8, AMBER, True)
    label(c, "src/simulation/scenario.py", 260, ROW5 - 26, SCEN_W, 7.5, GRAY)
    label(c, "Feature-space perturbations only", 260, ROW5 - 38, SCEN_W, 7, WHITE)
    label(c, "Risk can increase OR decrease", 260, ROW5 - 50, SCEN_W, 7, WHITE)
    label(c, "Labeled HYPOTHETICAL throughout", 260, ROW5 - 62, SCEN_W, 7, AMBER)

    # Arrows to dashboard
    arrow(c, 20 + PRED_W / 2, ROW5 - 68, 20 + PRED_W / 2, ROW5 - 68 - 18)
    arrow(c, 260 + SCEN_W / 2, ROW5 - 68, 260 + SCEN_W / 2, ROW5 - 68 - 18)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 6:  Auth + DB  +  Export
    # ─────────────────────────────────────────────────────────────────────────
    ROW6 = ROW5 - 68 - 18
    AUTH_W = 220
    EXP_W = 170

    box(c, 20, ROW6 - SMALL_H, AUTH_W, SMALL_H, PANEL_BG, RED)
    label(c, "AUTH & PERSISTENCE  (app/auth.py | src/database/db.py)", 20, ROW6 - 14, AUTH_W, 7.5, RED, True)
    label(c, "Argon2id hashing | SQLite | Workspace isolation | Parameterized SQL", 20, ROW6 - 26, AUTH_W, 7, WHITE)
    label(c, "instance/glycotwin.db (excluded from git)", 20, ROW6 - 36, AUTH_W, 6.5, GRAY)

    box(c, 250, ROW6 - SMALL_H, EXP_W, SMALL_H, PANEL_BG, PURPLE)
    label(c, "EXPORT  (src/simulation/export.py)", 250, ROW6 - 14, EXP_W, 7.5, PURPLE, True)
    label(c, "PDF session report | CSV timeline", 250, ROW6 - 26, EXP_W, 7, WHITE)
    label(c, "Research disclaimer in every export", 250, ROW6 - 36, EXP_W, 6.5, GRAY)

    # Arrow from dashboard to auth/export
    arrow(c, 620 + 205 / 2, TOP - BOX_H, 620 + 205 / 2, ROW6 + SMALL_H)

    # ─────────────────────────────────────────────────────────────────────────
    # Evaluation panel (right side)
    # ─────────────────────────────────────────────────────────────────────────
    EVAL_X = 490
    EVAL_W = 335
    EVAL_TOP = ROW2 - SMALL_H - 10

    box(c, EVAL_X, EVAL_TOP - 130, EVAL_W, 130, PANEL_BG, BLUE, radius=5)
    label(c, "VERIFIED TEST SET METRICS", EVAL_X, EVAL_TOP - 14, EVAL_W, 8, BLUE, True)
    label(c, "data/processed/baseline_results.csv", EVAL_X, EVAL_TOP - 26, EVAL_W, 7.5, GRAY)
    label(c, "AUROC:            0.7566", EVAL_X, EVAL_TOP - 40, EVAL_W, 8, WHITE)
    label(c, "Avg Precision:    0.4666", EVAL_X, EVAL_TOP - 52, EVAL_W, 8, WHITE)
    label(c, "F1 (@ 0.20):      0.4820", EVAL_X, EVAL_TOP - 64, EVAL_W, 8, WHITE)
    label(c, "Recall (@ 0.20):  0.7305", EVAL_X, EVAL_TOP - 76, EVAL_W, 8, WHITE)
    label(c, "Precision (@ 0.20): 0.3597", EVAL_X, EVAL_TOP - 88, EVAL_W, 8, WHITE)
    label(c, "Brier Score:      0.1439", EVAL_X, EVAL_TOP - 100, EVAL_W, 8, WHITE)
    label(c, "Ablation: +1.3 AUROC pts from personal baseline", EVAL_X, EVAL_TOP - 115, EVAL_W, 7.5, TEAL)
    label(c, "7-participant test set — wide confidence intervals", EVAL_X, EVAL_TOP - 127, EVAL_W, 7, AMBER)

    # ─────────────────────────────────────────────────────────────────────────
    # Safety panel (bottom right)
    # ─────────────────────────────────────────────────────────────────────────
    SAFE_TOP = EVAL_TOP - 130 - 12
    box(c, EVAL_X, SAFE_TOP - 75, EVAL_W, 75, PANEL_BG, RED, radius=5)
    label(c, "SAFETY & REGULATORY STATUS", EVAL_X, SAFE_TOP - 14, EVAL_W, 8, RED, True)
    label(c, "NOT a medical device", EVAL_X, SAFE_TOP - 28, EVAL_W, 8, WHITE)
    label(c, "NOT clinically validated", EVAL_X, SAFE_TOP - 40, EVAL_W, 8, WHITE)
    label(c, "NOT approved by FDA / CE / CDSCO", EVAL_X, SAFE_TOP - 52, EVAL_W, 8, WHITE)
    label(c, "Research prototype — Happiest Health Challenge 2026", EVAL_X, SAFE_TOP - 64, EVAL_W, 7.5, AMBER)

    # ─────────────────────────────────────────────────────────────────────────
    # Footer
    # ─────────────────────────────────────────────────────────────────────────
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, 14,
        "GlycoTwin Architecture v1.0  |  Python 3.10  |  scikit-learn  |  Streamlit  |  "
        "Dataset: PhysioNet CGMacros v1.0.0 (CC BY-NC-SA 4.0)  |  "
        "Code: MIT License  |  2026-10-19")

    c.save()
    print(f"Architecture PDF saved: {OUTPUT_PATH}")
    return str(OUTPUT_PATH)


if __name__ == "__main__":
    build_pdf()
