import json
import os
import tempfile

import plotly.graph_objects as go
import streamlit as st

from data_extractor import extract_parameters
from data_validator import validate_data
from input_parser import parse_input
from models.parameter_interpreter import interpret_parameters, interpret_severity
from models.panel_detector import detect_test_panels
from models.panel_interpreter import analyze_panels
from models.pattern_analyzer import (
    calculate_health_risk,
    detect_patterns,
    generate_recommendations,
)
from utils.metadata_extractor import extract_patient_metadata, fill_missing_metadata
from utils.standard_ranges import STANDARD_RANGES, UNITS
from utils.test_panels import TEST_PANELS

st.set_page_config(page_title="Health Report", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ui-bg: #0F172A;
        --card-bg: #111827;
        --card-bg-soft: #1E293B;
        --card-border: #1F2937;
        --text-primary: #E5E7EB;
        --text-secondary: #9CA3AF;
        --primary-blue: #2563EB;
        --normal-green: #22C55E;
        --high-red: #EF4444;
        --low-orange: #F59E0B;
        --shadow: 0 10px 25px rgba(0,0,0,0.35);
        --space-2: 8px;
        --space-4: 12px;
        --space-6: 16px;
        --space-8: 20px;
    }
    .stApp {
        background: var(--ui-bg);
    }
    [data-testid="stHeader"] {
        display: none;
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
    }
    .main-header {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(37,99,235,0.25);
    }
    .sub-title {
        text-align: center;
        color: var(--text-secondary);
        font-size: 16px;
        margin: 6px 0 6px 0;
    }
    .hero-note {
        text-align: center;
        color: var(--text-secondary);
        font-size: 14px;
        margin-bottom: 12px;
    }
    .metrics-wrap {
        margin-top: 0.25rem;
        margin-bottom: 0.6rem;
    }
    .metric-card {
        border: 1px solid var(--card-border);
        background: linear-gradient(145deg, #111827, #0f172a);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        min-height: 104px;
    }
    .metric-card:hover {
        transform: translateY(-4px) scale(1.01);
        transition: 0.2s;
    }
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 600;
    }
    .metric-value {
        margin-top: 0.35rem;
        font-size: 2rem;
        line-height: 1.1;
        font-weight: 800;
        color: var(--text-primary);
    }
    .risk-card {
        border-radius: 18px;
        padding: 18px;
        margin: 6px 0 10px 0;
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 600;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.12);
    }
    .risk-high {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    }
    .risk-medium {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    }
    .risk-low {
        background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
    }
    .risk-headline {
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    .risk-subtext {
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    .risk-score {
        font-size: 0.95rem;
        font-weight: 700;
    }
    .section-title {
        margin-top: 14px;
        margin-bottom: 0.45rem;
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--text-primary);
    }
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--card-border), transparent);
        margin: 12px 0;
    }
    .summary-table {
        border: 1px solid var(--card-border);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 0.5rem;
        background: var(--card-bg);
    }
    .summary-row {
        display: grid;
        grid-template-columns: 1.7fr 1fr 1fr 1fr 0.9fr;
        gap: 12px;
        align-items: center;
        padding: 14px 16px;
        border-bottom: 1px solid var(--card-border);
    }
    .summary-row:nth-child(even) {
        background: #0F172A;
    }
    .summary-row:last-child {
        border-bottom: none;
    }
    .summary-head {
        background: var(--card-bg-soft);
        font-weight: 700;
        color: var(--text-secondary);
    }
    .param-name {
        font-weight: 600;
        color: var(--text-primary);
    }
    .param-value {
        font-weight: 700;
        color: var(--text-primary);
    }
    .insight-card {
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 10px 12px;
        margin-bottom: 0.5rem;
        background: var(--card-bg-soft);
        color: var(--text-primary);
    }
    .insight-ok {
        background: #0B1F15;
        border-color: #14532D;
        color: #BBF7D0;
    }
    .insight-warn {
        background: #2A1F05;
        border-color: #92400E;
        color: #FDE68A;
    }
    .insight-danger {
        background: #3F0F16;
        border-color: #7F1D1D;
        color: #FECACA;
    }
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #FFFFFF;
    }
    .tag-normal {
        background: var(--normal-green);
    }
    .tag-high {
        background: var(--high-red);
    }
    .tag-low {
        background: var(--low-orange);
    }
    .key-findings {
        border: 1px solid var(--card-border);
        border-left: 5px solid var(--primary-blue);
        border-radius: 16px;
        padding: 10px 12px;
        background: #111827;
        margin-bottom: 8px;
    }
    .key-findings ul {
        margin: 0;
        padding-left: 20px;
    }
    .key-findings li {
        margin: 2px 0;
        color: var(--text-primary);
    }
    .rec-card {
        border: 1px solid var(--card-border);
        border-radius: 16px;
        background: var(--card-bg);
        padding: 8px 10px;
        margin-bottom: 6px;
    }
    .rec-head {
        font-weight: 700;
        color: var(--primary-blue);
        margin-bottom: 6px;
    }
    .report-actions {
        margin-top: 0.6rem;
    }
    .upload-box {
        border: 2px dashed #334155;
        padding: 16px 14px;
        border-radius: 16px;
        background: var(--card-bg);
        margin-bottom: 8px;
        text-align: center;
    }
    .input-panel {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 16px;
        padding: 12px;
        margin: 10px 0;
    }
    .input-head {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    .input-title {
        font-size: 18px;
        font-weight: 600;
        color: #F3F4F6;
    }
    .input-sub {
        font-size: 14px;
        color: #9CA3AF;
    }
    .category-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .category-head {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .profile-card {
        border: 1px solid var(--card-border);
        border-radius: 14px;
        background: var(--card-bg);
        padding: 12px;
        color: var(--text-primary);
        margin: 8px 0 14px 0;
    }
    .summary-card {
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 16px;
        background: linear-gradient(145deg, #111827, #0f172a);
        margin-bottom: 12px;
    }
    .summary-headline {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    @media screen and (max-width: 768px) {
        .section-title {
            font-size: 18px;
        }
        .risk-card {
            padding: 20px;
        }
        .risk-headline {
            font-size: 20px;
        }
        .summary-row {
            grid-template-columns: 1fr;
            gap: 8px;
        }
        .summary-head {
            display: none;
        }
        .block-container {
            padding-left: 12px !important;
            padding-right: 12px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='main-header'>Blood Report Analyzer</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'></div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='hero-note'></div>",
    unsafe_allow_html=True,
)


def run_pipeline(file_path, context):
    raw_input = parse_input(file_path)
    patient_metadata = extract_patient_metadata(raw_input)
    patient_metadata = fill_missing_metadata(
        patient_metadata,
        fallback_context=context,
        seed=file_path,
    )
    extracted = extract_parameters(raw_input)
    return analyze_values(extracted, context=context, patient_metadata=patient_metadata)


def analyze_values(raw_values, context, patient_metadata=None):
    patient_metadata = fill_missing_metadata(
        patient_metadata or {},
        fallback_context=context,
        seed="manual-entry",
    )
    clean_data = validate_data(raw_values)

    effective_context = dict(context or {})
    if patient_metadata.get("patient_name") and not effective_context.get("patient_name"):
        effective_context["patient_name"] = patient_metadata["patient_name"]
    if patient_metadata.get("age") and not effective_context.get("age"):
        effective_context["age"] = patient_metadata["age"]
    if patient_metadata.get("gender") and not effective_context.get("gender"):
        effective_context["gender"] = patient_metadata["gender"]

    interpretation = interpret_parameters(clean_data, context=effective_context)
    severity = interpret_severity(clean_data, context=effective_context)

    panels = detect_test_panels(clean_data)
    panel_results = analyze_panels(clean_data, panels)

    patterns = detect_patterns(clean_data, panels=panels)
    risk = calculate_health_risk(clean_data, panels=panels)
    recommendations = generate_recommendations(clean_data, interpretation)

    return {
        "values": clean_data,
        "interpretation": interpretation,
        "severity": severity,
        "patterns": patterns,
        "risk": risk,
        "panels": panels,
        "panel_results": panel_results,
        "recommendations": recommendations,
        "patient_metadata": patient_metadata,
        "patient_context": context,
        "effective_context": effective_context,
    }


def status_label(status):
    if status == "NORMAL":
        return "<span class='tag tag-normal'>NORMAL</span>"
    if status == "HIGH":
        return "<span class='tag tag-high'>HIGH</span>"
    return "<span class='tag tag-low'>LOW</span>"


def risk_class(level):
    if level == "HIGH":
        return "risk-high"
    if level == "MEDIUM":
        return "risk-medium"
    return "risk-low"


def _parameter_icon(name):
    return {
        "Hemoglobin": "🩸",
        "Glucose": "🍬",
        "Cholesterol": "❤️",
        "WBC": "🛡️",
        "Creatinine": "🧪",
        "LDL": "🫀",
        "HDL": "💙",
        "Triglycerides": "⚗️",
        "Platelets": "🧬",
    }.get(name, "•")


def _range_label(param, context):
    low, high = STANDARD_RANGES[param]
    if param == "Hemoglobin":
        gender = str(context.get("gender", "")).lower()
        if gender == "male":
            low, high = 13.0, 17.0
        elif gender == "female":
            low, high = 12.0, 15.0
    return f"{low}-{high} {UNITS.get(param, '')}".strip()


def _risk_title(level):
    return {
        "LOW": "🟢 LOW RISK",
        "MEDIUM": "🟡 MODERATE RISK",
        "HIGH": "🔴 HIGH RISK",
    }.get(level, "LOW RISK")


def _key_findings(values, interpretation, patterns, risk):
    findings = []
    for name, status in interpretation.items():
        if status == "HIGH":
            findings.append(f"Elevated {name} detected")
        elif status == "LOW":
            findings.append(f"Low {name} detected")

    if risk.get("derived_metrics", {}).get("ldl_hdl_assessment") in {"HIGH", "BORDERLINE"}:
        findings.append("LDL/HDL ratio above optimal range")

    for pattern in patterns:
        findings.append(pattern)

    if not findings:
        findings.append("No high-priority abnormalities detected")
    return findings[:6]


def _split_recommendations(recommendations):
    buckets = {"diet": [], "lifestyle": [], "medical": []}
    for text in recommendations:
        text_l = text.lower()
        if any(k in text_l for k in ["diet", "sugar", "fiber", "fat", "alcohol"]):
            buckets["diet"].append(text)
        elif any(k in text_l for k in ["exercise", "activity", "smoking", "weight"]):
            buckets["lifestyle"].append(text)
        else:
            buckets["medical"].append(text)
    return buckets


def _health_summary_text(risk_level, findings):
    lead = {
        "LOW": "Overall profile appears clinically stable.",
        "MEDIUM": "Some biomarkers need follow-up attention.",
        "HIGH": "Multiple abnormal signals require urgent clinical review.",
    }.get(risk_level, "Report processed with rule-based clinical checks.")
    if findings:
        return f"{lead} Key signal: {findings[0]}."
    return lead


def _missing_parameters(values):
    core = ["Glucose", "LDL", "HDL", "Triglycerides", "Creatinine", "WBC", "Hemoglobin"]
    return [param for param in core if param not in values]


def _build_professional_report(result):
    values = result["values"]
    interpretation = result["interpretation"]
    patterns = result["patterns"]
    risk = result["risk"]
    panels = result.get("panels", {})
    panel_results = result.get("panel_results", {})
    patient_metadata = result.get("patient_metadata", {})
    recommendations = result.get("recommendations", [])
    context = result.get("patient_context", {})

    lines = []
    lines.append("Health Report Summary")
    lines.append("---------------------")
    lines.append("")
    if patient_metadata:
        lines.append("Patient Information")
        if patient_metadata.get("patient_name"):
            lines.append(f"Name: {patient_metadata['patient_name']}")
        if patient_metadata.get("age"):
            lines.append(f"Age: {patient_metadata['age']}")
        if patient_metadata.get("gender"):
            lines.append(f"Gender: {str(patient_metadata['gender']).title()}")
        lines.append("")
    lines.append("Patient Context")
    lines.append(f"Age: {context.get('age', 'N/A')}")
    lines.append(f"Gender: {context.get('gender', 'N/A')}")
    lines.append(f"Weight (kg): {context.get('weight', 'N/A')}")
    lines.append("")

    lines.append("Patient Results")
    for name, value in values.items():
        status = interpretation.get(name, "UNKNOWN")
        unit = UNITS.get(name, "")
        lines.append(f"- {name}: {value} {unit} ({status})")
    lines.append("")

    lines.append("Detected Health Patterns")
    if patterns:
        for item in patterns:
            lines.append(f"- {item}")
    else:
        lines.append("- No major patterns detected")
    lines.append("")

    if panels:
        lines.append("Detected Blood Test Panels")
        for panel, info in panels.items():
            lines.append(f"- {panel}")
            missing = info.get("parameters_missing", [])
            if missing:
                lines.append(f"  * Missing: {', '.join(missing)}")
        lines.append("")

    if panel_results:
        lines.append("Panel-Based Analysis")
        for panel, findings in panel_results.items():
            lines.append(f"- {panel}:")
            if findings:
                if panel == "CBC":
                    suppress = {
                        "Possible anemia (low hemoglobin)",
                        "Possible infection/inflammation (high WBC)",
                        "Low platelet count",
                    }
                    findings = [f for f in findings if f not in suppress]
                for item in findings:
                    lines.append(f"  * {item}")
            else:
                lines.append("  * No abnormalities detected")
        lines.append("")

    lines.append("Risk Assessment")
    lines.append(f"- Risk Level: {risk['risk_level']}")
    lines.append(f"- Risk Score: {risk['risk_score']}")
    if risk.get("risk_factors"):
        lines.append("- Risk Factors:")
        for reason in risk["risk_factors"]:
            lines.append(f"  * {reason}")
    lines.append("")
    lines.append("Recommendations")
    for item in recommendations:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Disclaimer")
    lines.append("- This tool is rule-based and not a medical diagnosis.")
    lines.append("- Review all abnormal findings with a qualified clinician.")

    return "\n".join(lines)


def render_result(result):
    values = result["values"]
    interpretation = result["interpretation"]
    severity = result.get("severity", {})
    patterns = result["patterns"]
    risk = result["risk"]
    panels = result.get("panels", {})
    panel_results = result.get("panel_results", {})
    patient_metadata = result.get("patient_metadata", {})
    recommendations = result.get("recommendations", [])
    context = result.get("patient_context", {})

    st.markdown("<div class='section-title'>Result Dashboard</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>👤 Patient Information</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Name", patient_metadata.get("patient_name", "-") or "-")
    m2.metric("Age", patient_metadata.get("age", "-") or "-")
    gender = patient_metadata.get("gender", "")
    m3.metric("Gender", gender.title() if isinstance(gender, str) and gender else "-")
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    if not values:
        st.warning(
            "Could not extract enough values. Use Manual Entry mode for more accurate results."
        )
    else:
        pass

    normal_count = sum(1 for s in interpretation.values() if s == "NORMAL")
    abnormal_count = sum(1 for s in interpretation.values() if s != "NORMAL")
    findings = _key_findings(values, interpretation, patterns, risk)

    st.markdown("<div class='section-title'>AI Health Summary</div>", unsafe_allow_html=True)
    summary_text = risk.get("summary") or _health_summary_text(risk["risk_level"], findings)
    st.markdown(
        f"""
        <div class='summary-card'>
            <div class='summary-headline'>Risk Level: {risk['risk_level']}</div>
            <div>{summary_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='metrics-wrap'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>🧪 Parameters Found</div>
            <div class='metric-value'>{len(values)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>✅ Normal</div>
            <div class='metric-value'>{normal_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>⚠️ Out of Range</div>
            <div class='metric-value'>{abnormal_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c4.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>🧠 Patterns</div>
            <div class='metric-value'>{len(patterns)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    risk_message = {
        "LOW": "Overall indicators are within acceptable ranges.",
        "MEDIUM": "Multiple parameters require attention and close monitoring.",
        "HIGH": "Immediate medical consultation is recommended.",
    }.get(risk["risk_level"], "Your report has been evaluated with rule-based checks.")
    rc1, rc2 = st.columns([1.2, 1])
    with rc1:
        st.markdown(
            f"""
            <div class='risk-card {risk_class(risk['risk_level']).strip()}'>
                <div class='risk-headline'>{_risk_title(risk['risk_level'])}</div>
                <div class='risk-subtext'>{risk_message}</div>
                <div class='risk-score'>Risk Score: {risk['risk_score']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with rc2:
        gauge_max = max(10, risk["risk_score"] + 1)
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk["risk_score"],
                title={"text": "Health Risk Score"},
                gauge={
                    "axis": {"range": [0, gauge_max]},
                    "steps": [
                        {"range": [0, min(3, gauge_max)], "color": "#2ECC71"},
                        {"range": [min(3, gauge_max), min(6, gauge_max)], "color": "#F39C12"},
                        {"range": [min(6, gauge_max), gauge_max], "color": "#E74C3C"},
                    ],
                    "bar": {"color": "#E2E6EC"},
                },
            )
        )
        gauge.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=10),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(gauge, use_container_width=True)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🧠 Key Findings</div>", unsafe_allow_html=True)
    findings_html = "".join(f"<li>{item}</li>" for item in findings)
    st.markdown(f"<div class='key-findings'><ul>{findings_html}</ul></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Clinical Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Parameter Summary</div>", unsafe_allow_html=True)
    if values:
        st.markdown(
            """
            <div class='summary-table'>
                <div class='summary-row summary-head'>
                    <div>Parameter</div>
                    <div>Value</div>
                    <div>Reference Range</div>
                    <div>Status</div>
                    <div>Severity</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        for name, value in values.items():
            icon = _parameter_icon(name)
            ref_range = _range_label(name, context)
            sev = severity.get(name, "-")
            st.markdown(
                f"""
                <div class='summary-row'>
                    <div class='param-name'>{icon} {name}</div>
                    <div class='param-value'>{value} {UNITS.get(name, '')}</div>
                    <div>{ref_range}</div>
                    <div>{status_label(interpretation.get(name, 'LOW'))}</div>
                    <div>{sev}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    if panels:
        st.markdown("<div class='section-title'>🧾 Detected Blood Test Panels</div>", unsafe_allow_html=True)
        for panel, info in panels.items():
            st.markdown(
                f"<div class='insight-card insight-warn'><strong>{panel}</strong></div>",
                unsafe_allow_html=True,
            )
            missing = info.get("parameters_missing", [])
            if missing:
                st.markdown(
                    f"<div class='insight-card insight-ok'>Missing parameters: {', '.join(missing)}</div>",
                    unsafe_allow_html=True,
                )
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>🧪 Panel-Based Analysis</div>", unsafe_allow_html=True)
        for panel in panels.keys():
            st.markdown(f"<div class='section-title'>{panel}</div>", unsafe_allow_html=True)
            for param in TEST_PANELS.get(panel, []):
                if param in values:
                    status = interpretation.get(param, "NORMAL")
                    value = values.get(param)
                    sev = severity.get(param, "NORMAL")
                    klass = (
                        "insight-ok"
                        if status == "NORMAL"
                        else "insight-danger"
                        if status == "HIGH"
                        else "insight-warn"
                    )
                    st.markdown(
                        f"<div class='insight-card {klass}'>{param}: {value} {UNITS.get(param, '')} {status_label(status)} <span style='margin-left:8px; opacity:0.85;'>Severity: {sev}</span></div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div class='insight-card insight-warn'>{param}: Missing</div>",
                        unsafe_allow_html=True,
                    )

            findings = panel_results.get(panel, [])
            if findings:
                if panel == "CBC":
                    suppress = {
                        "Possible anemia (low hemoglobin)",
                        "Possible infection/inflammation (high WBC)",
                        "Low platelet count",
                    }
                    findings = [f for f in findings if f not in suppress]
                for item in findings:
                    st.warning(item)
            else:
                st.success("No abnormalities detected")
            st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Insights</div>", unsafe_allow_html=True)
    derived = risk.get("derived_metrics", {})
    if derived:
        st.markdown("<div class='section-title'>🧪 Derived Medical Metrics</div>", unsafe_allow_html=True)
        if "cholesterol_hdl_ratio" in derived:
            st.markdown(
                f"<div class='insight-card insight-warn'>Cholesterol/HDL Ratio: {derived['cholesterol_hdl_ratio']} ({derived.get('cholesterol_hdl_assessment', 'NA')})</div>",
                unsafe_allow_html=True,
            )
        if "ldl_hdl_ratio" in derived:
            st.markdown(
                f"<div class='insight-card insight-warn'>LDL/HDL Ratio: {derived['ldl_hdl_ratio']} ({derived.get('ldl_hdl_assessment', 'NA')})</div>",
                unsafe_allow_html=True,
            )
        if "non_hdl_cholesterol" in derived:
            st.markdown(
                f"<div class='insight-card insight-warn'>Non-HDL Cholesterol: {derived['non_hdl_cholesterol']} ({derived.get('non_hdl_assessment', 'NA')})</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🧬 Detected Patterns</div>", unsafe_allow_html=True)
    if patterns:
        for item in patterns:
            st.markdown(f"<div class='insight-card insight-warn'>- {item}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='insight-card insight-ok'>No major risk patterns detected from extracted parameters.</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>⚠ Risk Factors</div>", unsafe_allow_html=True)
    if risk["risk_factors"]:
        for reason in risk["risk_factors"]:
            st.markdown(f"<div class='insight-card insight-danger'>- {reason}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='insight-card insight-ok'>No strong risk factors detected.</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>💡 Recommendations</div>", unsafe_allow_html=True)
    grouped = _split_recommendations(recommendations)
    st.markdown("<div class='rec-card'><div class='rec-head'>🍎 Dietary Advice</div></div>", unsafe_allow_html=True)
    if grouped["diet"]:
        for item in grouped["diet"]:
            st.markdown(f"- {item}")
    else:
        st.markdown("- Maintain balanced nutrition and reduce processed foods.")
    st.markdown("<div class='rec-card'><div class='rec-head'>🏃 Lifestyle</div></div>", unsafe_allow_html=True)
    if grouped["lifestyle"]:
        for item in grouped["lifestyle"]:
            st.markdown(f"- {item}")
    else:
        st.markdown("- Aim for regular exercise and adequate sleep.")
    st.markdown("<div class='rec-card'><div class='rec-head'>👨‍⚕️ Medical</div></div>", unsafe_allow_html=True)
    if grouped["medical"]:
        for item in grouped["medical"]:
            st.markdown(f"- {item}")
    else:
        st.markdown("- Continue routine preventive checkups.")
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    with st.expander("How to read this"):
        st.write("NORMAL: within reference range")
        st.write("HIGH/LOW: outside reference range")
        st.write("Patterns: combined signal from multiple parameters")
        st.write("Risk Score: rule-based score, not a final medical diagnosis")

    st.markdown("<div class='section-title'>📥 Report Downloads</div>", unsafe_allow_html=True)
    st.markdown("<div class='report-actions'>", unsafe_allow_html=True)
    d1, d2 = st.columns([1, 1])
    d1.download_button(
        label="Download Full Report",
        data=json.dumps(result, indent=4),
        file_name="analysis_results_milestone2.json",
        mime="application/json",
        use_container_width=True,
    )
    d2.download_button(
        label="View Raw Data (JSON)",
        data=json.dumps(result, indent=4),
        file_name="analysis_results_raw.json",
        mime="application/json",
        use_container_width=True,
    )
    st.download_button(
        label="Download Professional Summary (TXT)",
        data=_build_professional_report(result),
        file_name="health_report_summary.txt",
        mime="text/plain",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def create_manual_entry_form():
    st.markdown("<div class='section-title'> Manual Data Entry</div>", unsafe_allow_html=True)

    categories = {
        "🩸 Complete Blood Count": ["Hemoglobin", "WBC", "Platelets"],
        "❤️ Lipid Panel": ["Cholesterol", "LDL", "HDL", "Triglycerides"],
        "🧪 Metabolic Panel": ["Glucose", "Creatinine"],
    }

    values = {}
    validation_messages = []

    with st.form("manual_entry_form"):
        cols = st.columns(2)
        category_names = list(categories.keys())
        for idx, category in enumerate(category_names):
            with cols[idx % 2]:
                st.markdown(f"<div class='category-card'><div class='category-head'>{category}</div>", unsafe_allow_html=True)
                for param in categories[category]:
                    low, high = STANDARD_RANGES[param]
                    unit = UNITS.get(param, "")
                    raw = st.text_input(
                        f"{param}",
                        key=f"manual_{param}",
                        placeholder=f"ref: {low}-{high} {unit}",
                        help=f"Reference range: {low}-{high} {unit}",
                    )
                    if raw.strip():
                        try:
                            numeric = float(raw.strip())
                            if numeric <= 0:
                                validation_messages.append(f"{param}: value should be positive")
                            else:
                                values[param] = numeric
                        except ValueError:
                            validation_messages.append(f"{param}: enter a valid number")
                st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("🔍 Analyze Values", use_container_width=True)

    if validation_messages:
        with st.expander("Validation Messages"):
            for message in validation_messages:
                st.markdown(f"- {message}")

    return values, submitted


with st.sidebar:
    st.header("Patient Information")
    age_input = st.number_input(
        "Age (years)",
        min_value=0,
        max_value=120,
        value=35,
        step=1,
        help="Enter patient's age in years for age-specific reference ranges",
    )
    gender_input = st.selectbox(
        "Biological Sex",
        ["Not specified", "Male", "Female"],
        help="Used for sex-specific ranges where applicable",
    )
    weight_input = st.number_input(
        "Weight (kg)",
        min_value=0.0,
        max_value=300.0,
        value=70.0,
        step=0.1,
        help="Weight in kilograms",
    )

    gender_icon = "👤" if gender_input == "Not specified" else "♂️" if gender_input == "Male" else "♀️"
    st.markdown("### Current Profile")
    st.markdown(
        f"""
        <div class='profile-card'>
            <div><strong>{gender_icon} Patient Profile</strong></div>
            <div>Age: {age_input} years</div>
            <div>Sex: {gender_input}</div>
            <div>Weight: {weight_input} kg</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if gender_input != "Not specified" and age_input > 0:
        st.info(f"Using {gender_input.lower()}-specific ranges for applicable parameters.")

patient_context = {
    "age": int(age_input),
    "gender": gender_input.lower() if gender_input != "Not specified" else "",
    "weight": float(weight_input),
}



input_mode = st.radio(
    "Select input method:",
    ["📄 Upload Report File", "✏️ Manual Data Entry"],
    horizontal=True,
)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

if input_mode == "📄 Upload Report File":
    st.markdown("### Upload Blood Report")
    st.caption("Supported: PDF, PNG, JPG, JPEG, JSON")
    uploaded_file = st.file_uploader(
        "Choose a blood report file",
        type=["pdf", "png", "jpg", "jpeg", "json"],
        help="Supported formats: PDF, PNG, JPG, JPEG, JSON",
    )

    if uploaded_file:
        ext = os.path.splitext(uploaded_file.name)[1]
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_path = temp_file.name
            with st.spinner("Analyzing medical parameters..."):
                render_result(run_pipeline(temp_path, context=patient_context))
        except Exception as exc:
            st.error(f"Failed to process file: {exc}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

if input_mode == "✏️ Manual Data Entry":
    manual_values, submitted = create_manual_entry_form()
    if submitted:
        if not manual_values:
            st.error("Please enter at least one valid value.")
        else:
            with st.spinner("Analyzing medical parameters..."):
                render_result(analyze_values(manual_values, context=patient_context))

st.markdown("")
st.markdown(
    ""
)
