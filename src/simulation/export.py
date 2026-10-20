"""
GlycoTwin — Report Export Utilities
Generates PDF and CSV session reports.

Reports include:
  - Research disclaimer
  - Participant ID (anonymous dataset ID only)
  - Twin state snapshots
  - Model estimates
  - Model version and data provenance
  - Scenario inputs and outputs (labeled as hypothetical)

Reports do NOT include:
  - User passwords, hashes, or secrets
  - Real patient PII
  - Treatment recommendations
"""

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ── reportlab imports ─────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ── Color scheme ─────────────────────────────────────────────────────────────
TEAL = colors.HexColor("#0d9488")
NAVY = colors.HexColor("#0f172a")
SLATE = colors.HexColor("#475569")
LIGHT = colors.HexColor("#f8fafc")
RED = colors.HexColor("#dc2626")


def _build_disclaimer_text() -> str:
    return (
        "RESEARCH PROTOTYPE — NOT A DIAGNOSTIC DEVICE. "
        "GlycoTwin is a proof-of-concept system built for the "
        "Happiest Health Digital Twin Challenge 2026. "
        "Model estimates are not clinical diagnoses or treatment recommendations. "
        "The 20% operating threshold is a research choice, not a clinically validated "
        "decision boundary. External and prospective validation would be required "
        "before any clinical use. "
        "Do not use this output to change medication, diet, or clinical management "
        "without consulting a qualified healthcare professional."
    )


def generate_pdf_report(
    participant_id: str,
    cohort: str,
    replay_rows: List[Dict[str, Any]],
    model_version: str = "glycotwin_logistic_calibrated",
    scenario_result: Optional[Dict[str, Any]] = None,
    user_display_name: str = "Research User",
) -> bytes:
    """
    Build a PDF session report and return raw bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "GlycoTitle",
        parent=styles["Heading1"],
        textColor=TEAL,
        fontSize=20,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "GlycSub",
        parent=styles["Normal"],
        textColor=SLATE,
        fontSize=10,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "GlycoSection",
        parent=styles["Heading2"],
        textColor=NAVY,
        fontSize=12,
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "GlycoBody",
        parent=styles["Normal"],
        fontSize=9,
        textColor=SLATE,
        leading=14,
    )
    disclaimer_style = ParagraphStyle(
        "GlycoDisclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=RED,
        leading=12,
        borderPadding=8,
    )

    story = []
    export_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("🧬 GlycoTwin Research Session Report", title_style))
    story.append(Paragraph(
        f"Personalized Bio-Digital Twin for 2-Hour Glucose Excursion Risk Prediction",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL))
    story.append(Spacer(1, 0.3 * cm))

    # ── Disclaimer ────────────────────────────────────────────────────────────
    story.append(Paragraph("⚠️ RESEARCH DISCLAIMER", section_style))
    story.append(Paragraph(_build_disclaimer_text(), disclaimer_style))
    story.append(Spacer(1, 0.4 * cm))

    # ── Session metadata ──────────────────────────────────────────────────────
    story.append(Paragraph("Session Metadata", section_style))
    meta_data = [
        ["Field", "Value"],
        ["Participant ID (Dataset)", str(participant_id)],
        ["Cohort", cohort],
        ["Model Version", model_version],
        ["Dataset", "PhysioNet CGMacros v1.0.0"],
        ["Target Definition", "≥30 mg/dL rise within 120 minutes"],
        ["Operating Threshold", "20% (research choice, not clinical)"],
        ["Exported by", user_display_name],
        ["Export Timestamp", export_time],
    ]
    meta_table = Table(meta_data, colWidths=[5 * cm, 11 * cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Replay data ───────────────────────────────────────────────────────────
    if replay_rows:
        story.append(Paragraph("Twin State Replay Snapshots", section_style))
        story.append(Paragraph(
            "Each row represents one 5-minute replay observation and the "
            "model's risk estimate at that point. All probabilities are "
            "model outputs, not clinical measurements.",
            body_style,
        ))
        story.append(Spacer(1, 0.2 * cm))

        # Build table
        headers = ["Timestamp", "Glucose\n(mg/dL)", "Baseline\n(mg/dL)",
                   "Momentum", "2-Hr Risk", "Confidence"]
        table_data = [headers]
        for row in replay_rows[-50:]:  # cap at 50 rows
            table_data.append([
                str(row.get("timestamp", "—"))[:16],
                f"{row.get('glucose', '—'):.0f}" if row.get("glucose") else "—",
                f"{row.get('personal_baseline', '—'):.1f}" if row.get("personal_baseline") else "—",
                f"{row.get('glucose_momentum', 0):+.1f}",
                f"{row.get('risk_probability', 0):.1%}",
                f"{row.get('data_confidence', 0):.0%}",
            ])

        replay_table = Table(table_data, colWidths=[3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        replay_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(replay_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Scenario results ──────────────────────────────────────────────────────
    if scenario_result:
        story.append(Paragraph("Hypothetical Scenario Results", section_style))
        story.append(Paragraph(
            "⚠️ HYPOTHETICAL ESTIMATES ONLY. These are feature-space "
            "perturbations run through the research model. They are NOT "
            "causal counterfactuals or clinical predictions. "
            "Risk may increase or decrease; neither outcome is a recommendation.",
            disclaimer_style,
        ))
        story.append(Spacer(1, 0.2 * cm))

        sc_data = [
            ["Field", "Value"],
            ["Scenario", scenario_result.get("scenario_name", "—")],
            ["Baseline Probability", f"{scenario_result.get('baseline_probability', 0):.1%}"],
            ["Scenario Probability", f"{scenario_result.get('scenario_probability', 0):.1%}"],
            ["Change (percentage points)", f"{scenario_result.get('delta_percentage_points', 0):+.1f} pp"],
            ["Modifications", str(scenario_result.get("modifications", {}))],
        ]
        sc_table = Table(sc_data, colWidths=[6 * cm, 10 * cm])
        sc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), TEAL),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
        ]))
        story.append(sc_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "GlycoTwin — Happiest Health Digital Twin Challenge 2026 | "
        "Dataset: PhysioNet CGMacros v1.0.0 (CC BY-NC-SA 4.0) | "
        "This report is for research purposes only.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7, textColor=SLATE),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def generate_csv_report(
    participant_id: str,
    replay_rows: List[Dict[str, Any]],
    model_version: str = "glycotwin_logistic_calibrated",
) -> str:
    """Return CSV string of the session replay data."""
    output = io.StringIO()
    output.write(f"# GlycoTwin Research Session Report\n")
    output.write(f"# Participant: {participant_id}\n")
    output.write(f"# Model: {model_version}\n")
    output.write(f"# Dataset: PhysioNet CGMacros v1.0.0\n")
    output.write(f"# Exported: {datetime.now(timezone.utc).isoformat()} UTC\n")
    output.write(f"# RESEARCH PROTOTYPE — NOT A CLINICAL REPORT\n")
    output.write("\n")

    if not replay_rows:
        output.write("No replay data available.\n")
        return output.getvalue()

    fieldnames = [
        "timestamp", "glucose", "heart_rate", "activity_calories", "mets",
        "personal_baseline", "glucose_momentum", "data_confidence",
        "risk_probability", "excursion_risk",
    ]
    writer = csv.DictWriter(
        output, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    for row in replay_rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})

    return output.getvalue()
