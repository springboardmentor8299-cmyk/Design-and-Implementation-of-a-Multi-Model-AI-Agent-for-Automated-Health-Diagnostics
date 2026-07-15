# backend/report_generator.py
"""
Report Generation Module
Generates a formatted PDF report using reportlab.
"""

import io
from datetime import datetime


def generate_pdf_report(
    parameters: dict,
    classified: list,
    patterns: list,
    scores: dict,
    predictions: list,
    recommendations: dict,
    metadata: dict = None,
) -> bytes:
    """
    Generates a PDF health report and returns it as bytes.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        raise ImportError("reportlab is required. Run: pip install reportlab")

    meta   = metadata or {}
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize    = A4,
        rightMargin = 2 * cm,
        leftMargin  = 2 * cm,
        topMargin   = 2 * cm,
        bottomMargin= 2 * cm,
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title",
        parent    = styles["Heading1"],
        fontSize  = 22,
        textColor = colors.HexColor("#1A5276"),
        spaceAfter= 6,
        alignment = TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent    = styles["Normal"],
        fontSize  = 10,
        textColor = colors.HexColor("#5D6D7E"),
        alignment = TA_CENTER,
        spaceAfter= 16,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent    = styles["Heading2"],
        fontSize  = 13,
        textColor = colors.HexColor("#1A5276"),
        spaceBefore= 14,
        spaceAfter = 4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent    = styles["Normal"],
        fontSize  = 9,
        leading   = 14,
    )
    warn_style = ParagraphStyle(
        "Warn",
        parent    = styles["Normal"],
        fontSize  = 8,
        textColor = colors.HexColor("#7F8C8D"),
        leading   = 12,
        alignment = TA_CENTER,
    )

    content = []

    # ── Header ───────────────────────────────────────────────────────────────
    content.append(Paragraph("Healytics", title_style))
    content.append(Paragraph("AI-Powered Blood Report Analysis", subtitle_style))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1A5276")))
    content.append(Spacer(1, 10))

    # Report date and patient info
    report_date = datetime.now().strftime("%d %B %Y, %I:%M %p")
    patient_info = [
        ["Report Date:", report_date],
        ["Patient:",     meta.get("patient_name", "N/A")],
        ["Age:",         str(meta.get("age", "N/A"))],
        ["Gender:",      str(meta.get("gender", "N/A")).capitalize()],
    ]
    pt = Table(patient_info, colWidths=[4 * cm, 12 * cm])
    pt.setStyle(TableStyle([
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",   (0, 0), (0, -1), colors.HexColor("#1A5276")),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ]))
    content.append(pt)
    content.append(Spacer(1, 10))
    content.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))

    # ── Health Score & Risk Summary ───────────────────────────────────────────
    content.append(Paragraph("Health Score & Risk Summary", h2_style))

    hs = scores.get("health_score", {})
    cv = scores.get("cardiovascular", {})
    db = scores.get("diabetes", {})
    kd = scores.get("kidney", {})
    lv = scores.get("liver", {})
    tc_hdl = scores.get("tc_hdl_ratio", {})

    summary_data = [
        ["Metric",               "Value",             "Category"],
        ["Overall Health Score", f"{hs.get('score','N/A')} / 100", hs.get('label','N/A')],
        ["Cardiovascular Risk",  f"{cv.get('risk_pct','N/A')}%",   cv.get('category','N/A')],
        ["Diabetes Risk",        f"{db.get('risk_pct','N/A')}%",   db.get('category','N/A')],
        ["Kidney Risk",          f"{kd.get('risk_pct','N/A')}%",   kd.get('category','N/A')],
        ["Liver Risk",           f"{lv.get('risk_pct','N/A')}%",   lv.get('category','N/A')],
        ["TC/HDL Ratio",         str(tc_hdl.get('ratio','N/A')),   tc_hdl.get('category','N/A')],
    ]
    st_table = Table(summary_data, colWidths=[7 * cm, 4 * cm, 5 * cm])
    st_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#1A5276")),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#EBF5FB"), colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING",      (0, 0), (-1, -1), 6),
    ]))
    content.append(st_table)
    content.append(Spacer(1, 8))

    # ── Parameter Classification ─────────────────────────────────────────────
    content.append(Paragraph("Parameter Classification", h2_style))

    param_data = [["Parameter", "Category", "Your Value", "Reference Range", "Status"]]
    for item in classified:
        val_str = f"{item['value']} {item['unit']}"
        param_data.append([
            item["display_name"],
            item["category"],
            val_str,
            item["ref_range_str"],
            item["status"],
        ])

    if len(param_data) > 1:
        col_widths = [5.5*cm, 3.5*cm, 3.5*cm, 4*cm, 2.5*cm]
        p_table = Table(param_data, colWidths=col_widths, repeatRows=1)
        style_cmds = [
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1A5276")),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#EBF5FB"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("PADDING",       (0, 0), (-1, -1), 4),
        ]
        for i, item in enumerate(classified, start=1):
            if item["severity"] == "critical":
                style_cmds.append(("BACKGROUND", (4, i), (4, i), colors.HexColor("#FADBD8")))
                style_cmds.append(("TEXTCOLOR",  (4, i), (4, i), colors.HexColor("#C0392B")))
            elif item["severity"] == "warning":
                style_cmds.append(("BACKGROUND", (4, i), (4, i), colors.HexColor("#FDEBD0")))
                style_cmds.append(("TEXTCOLOR",  (4, i), (4, i), colors.HexColor("#E67E22")))
        p_table.setStyle(TableStyle(style_cmds))
        content.append(p_table)

    content.append(Spacer(1, 8))

    # ── Detected Patterns ────────────────────────────────────────────────────
    if patterns:
        content.append(Paragraph("Detected Clinical Patterns", h2_style))
        for pat in patterns:
            content.append(Paragraph(f"<b>{pat['icon']} {pat['name']}</b> [{pat['severity'].upper()}]", body_style))
            content.append(Paragraph(pat["description"], body_style))
            for c in pat.get("criteria", []):
                content.append(Paragraph(f"  • {c}", body_style))
            content.append(Spacer(1, 5))

    # ── Disease Risk Predictions ──────────────────────────────────────────────
    if predictions:
        content.append(Paragraph("Disease Risk Predictions", h2_style))
        pred_data = [["Disease", "Risk %", "Category"]]
        for pred in predictions:
            pred_data.append([
                f"{pred['icon']} {pred['name']}",
                f"{pred['risk_pct']}%",
                pred["category"],
            ])
        pr_table = Table(pred_data, colWidths=[9*cm, 3*cm, 5*cm])
        pr_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1A5276")),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#EBF5FB"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("PADDING",       (0, 0), (-1, -1), 5),
        ]))
        content.append(pr_table)
        content.append(Spacer(1, 8))

    # ── Recommendations ───────────────────────────────────────────────────────
    content.append(Paragraph("Personalized Recommendations", h2_style))
    cat_labels = {
        "cardiovascular": "💙 Cardiovascular",
        "nutrition":      "🥗 Nutrition & Diet",
        "lifestyle":      "🏃 Lifestyle",
        "medical":        "⚕️ Medical",
    }
    for cat_key, cat_label in cat_labels.items():
        recs = recommendations.get(cat_key, [])
        if recs:
            content.append(Paragraph(f"<b>{cat_label}</b>", body_style))
            for r in recs:
                content.append(Paragraph(f"  {r['icon']} {r['text']}", body_style))
            content.append(Spacer(1, 5))

    # ── Disclaimer ────────────────────────────────────────────────────────────
    content.append(Spacer(1, 12))
    content.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    content.append(Spacer(1, 6))
    content.append(Paragraph(
        "⚠️ DISCLAIMER: This report is generated by an AI system and is intended for informational "
        "purposes ONLY. It does NOT constitute medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare professional for medical advice and before making "
        "any health decisions. Do not disregard professional medical advice based on this report.",
        warn_style,
    ))
    content.append(Paragraph(
        f"Generated by Healytics on {report_date}",
        warn_style,
    ))

    doc.build(content)
    buffer.seek(0)
    return buffer.read()