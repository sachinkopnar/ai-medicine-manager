"""
reports.py — Automatic Patient Medication Report (PDF).
Pulls together a profile's active medicines, weekly adherence, and
today's schedule into a clean, printable PDF — the kind you could
hand to a doctor at a check-up.
"""

from datetime import datetime, date
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

NAVY = colors.HexColor("#1a2a52")
TEAL = colors.HexColor("#0f9b8e")
LIGHT_GREY = colors.HexColor("#f2f4f8")
RED = colors.HexColor("#d64545")
GREEN = colors.HexColor("#2fa860")


def generate_medication_report(
    profile: dict,
    account_username: str,
    medicines: dict,
    stats: dict,
    weekly_adherence: dict,
) -> bytes:
    """
    Build a medication report PDF for one patient profile.
    Returns the PDF as raw bytes, ready for st.download_button.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], textColor=NAVY, fontSize=20, spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], textColor=colors.grey, fontSize=9, spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], textColor=TEAL, fontSize=13,
        spaceBefore=14, spaceAfter=6,
    )
    normal = styles["Normal"]

    story = []

    # ── Header ────────────────────────────────────────────────────────────
    story.append(Paragraph("💊 AI Medicine Manager", title_style))
    story.append(Paragraph("Patient Medication Report", subtitle_style))
    story.append(HRFlowable(width="100%", color=NAVY, thickness=1.2))
    story.append(Spacer(1, 10))

    # ── Patient info ──────────────────────────────────────────────────────
    story.append(Paragraph("Patient Information", section_style))
    patient_rows = [
        ["Name", profile.get("name", "-")],
        ["Relation", profile.get("relation", "-")],
        ["Age", profile.get("age", "-") or "-"],
        ["Gender", profile.get("gender", "-") or "-"],
        ["Account", account_username],
        ["Report generated", datetime.now().strftime("%d %b %Y, %I:%M %p")],
    ]
    patient_table = Table(patient_rows, colWidths=[45 * mm, 110 * mm])
    patient_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(patient_table)

    # ── Adherence summary ─────────────────────────────────────────────────
    story.append(Paragraph("Adherence Summary (Today)", section_style))
    summary_rows = [
        ["Total medicines", "Doses today", "Taken", "Missed", "Adherence"],
        [
            str(stats["total_medicines"]),
            str(stats["today_total"]),
            str(stats["today_taken"]),
            str(stats["today_missed"]),
            f"{stats['adherence_pct']}%",
        ],
    ]
    summary_table = Table(summary_rows, colWidths=[31 * mm] * 5)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(summary_table)

    # ── Current medicines ─────────────────────────────────────────────────
    story.append(Paragraph("Current Medicines", section_style))
    if not medicines:
        story.append(Paragraph("No active medicines on record.", normal))
    else:
        med_rows = [["Medicine", "Dosage", "Frequency", "Times", "Stock", "Notes"]]
        for med in medicines.values():
            stock = med.get("stock_quantity")
            stock_txt = str(stock) if stock is not None else "-"
            med_rows.append([
                Paragraph(med.get("name", "-"), normal),
                Paragraph(med.get("dosage", "-"), normal),
                Paragraph(med.get("frequency", "-"), normal),
                Paragraph(", ".join(med.get("times", [])), normal),
                Paragraph(stock_txt, normal),
                Paragraph(med.get("notes", "") or "-", normal),
            ])
        med_table = Table(med_rows, colWidths=[28 * mm, 20 * mm, 25 * mm, 24 * mm, 15 * mm, 44 * mm])
        med_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), TEAL),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        story.append(med_table)

    # ── 7-day adherence history ──────────────────────────────────────────
    story.append(Paragraph("7-Day Adherence History", section_style))
    hist_rows = [["Date", "Taken", "Missed", "Pending"]]
    for day, counts in weekly_adherence.items():
        hist_rows.append([
            day, str(counts["taken"]), str(counts["missed"]), str(counts["pending"]),
        ])
    hist_table = Table(hist_rows, colWidths=[45 * mm, 30 * mm, 30 * mm, 30 * mm])
    hist_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TEXTCOLOR", (1, 1), (1, -1), GREEN),
        ("TEXTCOLOR", (2, 1), (2, -1), RED),
    ]))
    story.append(hist_table)

    # ── Footer note ───────────────────────────────────────────────────────
    story.append(Spacer(1, 18))
    story.append(HRFlowable(width="100%", color=colors.lightgrey, thickness=0.7))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This report was generated automatically by AI Medicine Manager and is "
        "intended to support — not replace — discussions with a qualified healthcare provider.",
        ParagraphStyle("Footer", parent=normal, fontSize=7.5, textColor=colors.grey),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
