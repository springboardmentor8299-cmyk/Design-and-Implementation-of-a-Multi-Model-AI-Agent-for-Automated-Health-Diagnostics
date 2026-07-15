# app.py
"""
Healytics — Main Streamlit Application
Run with: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import sys
import os
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from backend.input_processor       import InputProcessor
from backend.parameter_classifier  import ParameterClassifier
from backend.pattern_detector      import PatternDetector
from backend.risk_scorer           import RiskScorer
from backend.recommendation_engine import RecommendationEngine
from backend.disease_predictor     import DiseasePredictor
from backend.report_generator      import generate_pdf_report
from backend.chatbot               import Chatbot
from backend.reference_ranges      import SAMPLE_REPORT, REFERENCE_RANGES

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Healytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ──────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global Reset ─────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Main Background ──────────────────────────────── */
.main { background: #F0F4F8; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1300px; }

/* ── Header ───────────────────────────────────────── */
.healthai-header {
    background: linear-gradient(135deg, #1A5276 0%, #154360 50%, #0E2F50 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(26,82,118,0.25);
}
.healthai-header h1 {
    color: #FFFFFF;
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.healthai-header p {
    color: #AED6F1;
    font-size: 1rem;
    margin: 0.4rem 0 0 0;
    font-weight: 300;
}
.header-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    color: #AED6F1;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    border: 1px solid rgba(255,255,255,0.2);
    margin-top: 0.5rem;
}

/* ── Cards ────────────────────────────────────────── */
.card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #E8EDF2;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
}
.card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.1); }

/* ── Input Option Cards ───────────────────────────── */
.input-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1.5rem 1rem;
    text-align: center;
    border: 2px solid #E8EDF2;
    cursor: pointer;
    transition: all 0.2s;
    height: 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}
.input-card:hover { border-color: #2E86C1; box-shadow: 0 4px 16px rgba(46,134,193,0.15); }
.input-card.active { border-color: #1A5276; background: #EBF5FB; }
.input-card-icon { font-size: 2rem; }
.input-card-title { font-weight: 600; font-size: 0.95rem; color: #1A5276; }
.input-card-sub { font-size: 0.75rem; color: #7F8C8D; }

/* ── Alert Boxes ──────────────────────────────────── */
.alert-critical {
    background: #FDEDEC;
    border-left: 4px solid #E74C3C;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    color: #922B21;
}
.alert-warning {
    background: #FEFCE8;
    border-left: 4px solid #F39C12;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    color: #7D6608;
}
.alert-info {
    background: #EBF5FB;
    border-left: 4px solid #2E86C1;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    color: #1A5276;
}

/* ── Metric Cards ─────────────────────────────────── */
.metric-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid #E8EDF2;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1A5276;
}
.metric-label {
    font-size: 0.78rem;
    color: #7F8C8D;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.2rem;
}

/* ── Status Badges ────────────────────────────────── */
.badge-normal   { background:#D5F5E3; color:#1E8449; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-high     { background:#FDEBD0; color:#E67E22; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-low      { background:#EBF5FB; color:#2E86C1; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-critical { background:#FADBD8; color:#E74C3C; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

/* ── Pattern Cards ────────────────────────────────── */
.pattern-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    border-left: 4px solid #E67E22;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 0.8rem;
}
.pattern-card.high     { border-left-color: #E74C3C; }
.pattern-card.moderate { border-left-color: #E67E22; }
.pattern-card.low      { border-left-color: #F39C12; }
.pattern-name { font-weight: 600; color: #1A5276; font-size: 0.95rem; }
.pattern-desc { color: #5D6D7E; font-size: 0.85rem; margin-top: 0.3rem; }

/* ── Risk Cards ───────────────────────────────────── */
.risk-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid #E8EDF2;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.risk-name { font-weight: 600; color: #1A5276; font-size: 0.85rem; }
.risk-pct  { font-size: 1.8rem; font-weight: 700; }
.risk-cat  { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

/* ── Recommendation Cards ─────────────────────────── */
.rec-item {
    background: #F8FBFF;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.4rem;
    border: 1px solid #E8EDF2;
    font-size: 0.88rem;
    color: #2C3E50;
    line-height: 1.5;
}

/* ── Chatbot ──────────────────────────────────────── */
.chat-container {
    background: #F8FBFF;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid #E8EDF2;
    min-height: 300px;
    max-height: 400px;
    overflow-y: auto;
}
.chat-msg-user {
    background: #1A5276;
    color: white;
    padding: 0.6rem 1rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.5rem 0 0.5rem 3rem;
    font-size: 0.88rem;
}
.chat-msg-bot {
    background: #FFFFFF;
    color: #2C3E50;
    padding: 0.6rem 1rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.5rem 3rem 0.5rem 0;
    font-size: 0.88rem;
    border: 1px solid #E8EDF2;
    white-space: pre-wrap;
}

/* ── Section Titles ───────────────────────────────── */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1A5276;
    margin: 0.5rem 0 0.8rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #AED6F1;
}

/* ── Disclaimer ───────────────────────────────────── */
.disclaimer {
    background: #FEF9E7;
    border: 1px solid #F9E79F;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    color: #7D6608;
    font-size: 0.82rem;
    line-height: 1.6;
    margin-top: 1.5rem;
}

/* ── Sidebar Overrides ────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E8EDF2;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #1A5276;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Streamlit Button Override ────────────────────── */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s;
}
div[data-testid="stHorizontalBlock"] .stButton > button {
    width: 100%;
}

/* ── Tab styling ──────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F0F4F8;
    padding: 4px;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.4rem 1rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "analysis_done":  False,
        "analysis_result": None,
        "chat_history":   [],
        "chatbot":        None,
        "input_mode":     "json",  # "json" | "manual" | "pdf"
        "manual_params":  {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
def run_analysis(parameters: dict, metadata: dict) -> dict:
    """Full analysis pipeline."""
    processor   = InputProcessor()
    classifier  = ParameterClassifier()
    detector    = PatternDetector()
    scorer      = RiskScorer()
    recommender = RecommendationEngine()
    predictor   = DiseasePredictor()

    # Validate
    validated = processor.validate({"parameters": parameters, "metadata": metadata})

    classified   = classifier.classify_all(validated["parameters"], metadata.get("gender", "general"))
    counts       = classifier.get_summary_counts(classified)
    patterns     = detector.detect_all(validated["parameters"], classified, metadata)
    scores       = scorer.calculate_all(validated["parameters"], classified, metadata)
    predictions  = predictor.predict_all(validated["parameters"], metadata)
    recs         = recommender.generate(classified, patterns, scores, metadata)

    return {
        "parameters":    validated["parameters"],
        "metadata":      metadata,
        "classified":    classified,
        "counts":        counts,
        "patterns":      patterns,
        "scores":        scores,
        "predictions":   predictions,
        "recommendations": recs,
        "warnings":      validated.get("warnings", []),
    }


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="healthai-header">
    <h1>🏥 Healytics</h1>
    <p>AI-powered blood report analysis and personalized health insights</p>
    <span class="header-badge">⚕️ For educational purposes only — Not a substitute for medical advice</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Patient Information
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Patient Information")

    patient_name = st.text_input("Patient Name (optional)", placeholder="e.g. John Doe")
    age = st.number_input("Age", min_value=1, max_value=120, value=40, step=1)
    gender = st.selectbox("Gender", ["general", "male", "female"], format_func=str.capitalize)
    medical_history = st.multiselect(
        "Known Conditions",
        [
            "Diabetes", "Hypertension", "Heart Disease", "Obesity",
            "Thyroid Disorder", "Kidney Disease", "Liver Disease",
            "Anemia", "High Cholesterol", "None"
        ],
        default=[]
    )

    st.markdown("---")
    st.markdown("### 📋 Sample Reports")
    st.caption("Load pre-built demo data to see the analysis in action.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("👨 Cardiac Risk\nProfile", use_container_width=True):
            st.session_state["demo_data"] = {
                "hemoglobin": 13.2, "wbc": 10.5, "platelets": 220,
                "total_cholesterol": 245, "ldl_cholesterol": 168, "hdl_cholesterol": 36,
                "triglycerides": 225, "glucose_fasting": 115, "hba1c": 6.2,
                "creatinine": 1.2, "bun": 22, "alt": 38, "ast": 35,
                "vitamin_d": 18, "crp": 9.5, "tsh": 3.2,
            }
            st.session_state["input_mode"] = "json"
            st.rerun()

    with col_s2:
        if st.button("👩 Anemia &\nThyroid", use_container_width=True):
            st.session_state["demo_data"] = {
                "hemoglobin": 10.5, "rbc": 3.8, "mcv": 72, "hematocrit": 32,
                "ferritin": 8, "iron": 45, "tibc": 390,
                "tsh": 6.8, "t4": 4.5, "free_t4": 0.75,
                "total_cholesterol": 195, "ldl_cholesterol": 120, "hdl_cholesterol": 52,
                "triglycerides": 140, "glucose_fasting": 88, "vitamin_b12": 185,
                "vitamin_d": 15, "creatinine": 0.8,
            }
            st.session_state["input_mode"] = "json"
            st.rerun()

    if st.button("🏥 Full Metabolic\nPanel Demo", use_container_width=True):
        st.session_state["demo_data"] = SAMPLE_REPORT
        st.session_state["input_mode"] = "json"
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        "Healytics uses multi-model AI to interpret blood reports, "
        "detect clinical patterns, and generate personalized recommendations."
    )
    if os.getenv("GROQ_API_KEY"):
        st.success("🤖 AI Chatbot: Active (Groq)")
    else:
        st.info("🤖 AI Chatbot: Rule-based mode\n(Add GROQ_API_KEY in .env for LLM mode)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT — Input Section
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📥 Choose Input Method</div>', unsafe_allow_html=True)

col_i1, col_i2, col_i3 = st.columns(3)

with col_i1:
    if st.button("📄 Upload JSON Report", use_container_width=True, type="primary" if st.session_state["input_mode"] == "json" else "secondary"):
        st.session_state["input_mode"] = "json"

with col_i2:
    if st.button("✏️ Enter Values Manually", use_container_width=True, type="primary" if st.session_state["input_mode"] == "manual" else "secondary"):
        st.session_state["input_mode"] = "manual"

with col_i3:
    if st.button("📑 Upload PDF Report", use_container_width=True, type="primary" if st.session_state["input_mode"] == "pdf" else "secondary"):
        st.session_state["input_mode"] = "pdf"

st.markdown("")

# ── JSON Upload Mode ──────────────────────────────────────────────────────────
if st.session_state["input_mode"] == "json":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📄 Upload JSON Blood Report**")
        st.caption("Upload a JSON file containing blood parameter names and values, or paste JSON text below.")

        # Pre-fill from demo if set
        demo_json = ""
        if "demo_data" in st.session_state:
            demo_json = json.dumps(st.session_state["demo_data"], indent=2)

        uploaded_json = st.file_uploader("Upload JSON file", type=["json"], key="json_upload")
        json_text     = st.text_area("Or paste JSON here", value=demo_json, height=200, placeholder='{"hemoglobin": 14.5, "glucose_fasting": 95, ...}')

        col_a, col_b = st.columns([1, 3])
        with col_a:
            analyze_json = st.button("🔍 Analyze", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if analyze_json:
        raw_data = None
        try:
            if uploaded_json:
                raw_data = json.loads(uploaded_json.read())
            elif json_text.strip():
                raw_data = json.loads(json_text)
            else:
                st.error("Please upload a JSON file or paste JSON data.")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")

        if raw_data:
            with st.spinner("🔬 Analyzing your blood report..."):
                processor = InputProcessor()
                processed = processor.process_json(raw_data)
                meta = {
                    "patient_name":    patient_name or processed["metadata"].get("patient_name", ""),
                    "age":             age or processed["metadata"].get("age", 40),
                    "gender":          gender or processed["metadata"].get("gender", "general"),
                    "medical_history": medical_history,
                }
                result = run_analysis(processed["parameters"], meta)
                st.session_state["analysis_result"] = result
                st.session_state["analysis_done"]   = True
                st.session_state["chatbot"]         = Chatbot(result)
                if "demo_data" in st.session_state:
                    del st.session_state["demo_data"]
                st.rerun()

# ── Manual Entry Mode ─────────────────────────────────────────────────────────
elif st.session_state["input_mode"] == "manual":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**✏️ Enter Blood Parameters Manually**")
        st.caption("Enter values for the parameters available in your report. Leave unused fields empty.")

        # Grouped by category
        categories = {}
        for key, ref in REFERENCE_RANGES.items():
            cat = ref.get("category", "Other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, ref))

        manual_values = {}
        for cat, params in sorted(categories.items()):
            with st.expander(f"📋 {cat}", expanded=(cat in ["CBC", "Lipid Panel", "Blood Sugar"])):
                cols = st.columns(3)
                for idx, (key, ref) in enumerate(params):
                    name = ref.get("display_name", key)
                    g_range = ref.get("general") or ref.get("male") or {}
                    unit = g_range.get("unit", "")
                    label = f"{name} ({unit})" if unit else name
                    with cols[idx % 3]:
                        val = st.number_input(label, min_value=0.0, value=0.0, format="%.2f",
                                              key=f"manual_{key}", step=0.1)
                        if val > 0:
                            manual_values[key] = val

        st.markdown("</div>", unsafe_allow_html=True)

        col_a, col_b = st.columns([1, 3])
        with col_a:
            analyze_manual = st.button("🔍 Analyze", type="primary", use_container_width=True)

    if analyze_manual:
        if not manual_values:
            st.warning("Please enter at least one blood parameter value.")
        else:
            with st.spinner("🔬 Analyzing your blood report..."):
                meta = {
                    "patient_name":    patient_name,
                    "age":             age,
                    "gender":          gender,
                    "medical_history": medical_history,
                }
                result = run_analysis(manual_values, meta)
                st.session_state["analysis_result"] = result
                st.session_state["analysis_done"]   = True
                st.session_state["chatbot"]         = Chatbot(result)
                st.rerun()

# ── PDF Upload Mode ───────────────────────────────────────────────────────────
elif st.session_state["input_mode"] == "pdf":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📑 Upload PDF Blood Report**")
        st.caption("Upload your blood report PDF. The AI will extract parameter values automatically using OCR.")
        st.info("💡 Tip: For best results, ensure the PDF is text-based (not a scanned image). Extraction accuracy may vary by report format.")

        uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"], key="pdf_upload")

        col_a, col_b = st.columns([1, 3])
        with col_a:
            analyze_pdf = st.button("🔍 Extract & Analyze", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if analyze_pdf:
        if not uploaded_pdf:
            st.error("Please upload a PDF file.")
        else:
            with st.spinner("📖 Extracting data from PDF... (this may take a moment)"):
                processor = InputProcessor()
                pdf_bytes = uploaded_pdf.read()
                processed = processor.process_pdf_bytes(pdf_bytes)

                if "error" in processed:
                    st.error(f"PDF processing error: {processed['error']}")
                elif not processed["parameters"]:
                    st.warning(
                        "Could not extract blood parameters from the PDF automatically. "
                        "The PDF format may not be supported. Please try Manual Entry instead."
                    )
                else:
                    st.success(f"✅ Extracted {len(processed['parameters'])} parameters from PDF!")
                    meta = {
                        "patient_name":    patient_name or processed["metadata"].get("patient_name", ""),
                        "age":             age or processed["metadata"].get("age", 40),
                        "gender":          gender or processed["metadata"].get("gender", "general"),
                        "medical_history": medical_history,
                    }
                    result = run_analysis(processed["parameters"], meta)
                    st.session_state["analysis_result"] = result
                    st.session_state["analysis_done"]   = True
                    st.session_state["chatbot"]         = Chatbot(result)
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS SECTION
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state["analysis_done"] and st.session_state["analysis_result"]:
    result = st.session_state["analysis_result"]
    classified   = result["classified"]
    patterns     = result["patterns"]
    scores       = result["scores"]
    predictions  = result["predictions"]
    recs         = result["recommendations"]
    counts       = result["counts"]
    meta         = result["metadata"]

    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    # ── Smart Alerts ──────────────────────────────────────────────────────────
    critical_items = [c for c in classified if c["severity"] == "critical"]
    warning_items  = [c for c in classified if c["severity"] == "warning"]

    if critical_items or warning_items:
        st.markdown('<div class="section-title">🚨 Smart Alerts</div>', unsafe_allow_html=True)
        for item in critical_items:
            st.markdown(
                f'<div class="alert-critical">🔴 <strong>CRITICAL:</strong> '
                f'{item["display_name"]} is {item["status"].upper()} — '
                f'Value: {item["value"]} {item["unit"]} (Ref: {item["ref_range_str"]}). '
                f'Seek medical attention.</div>',
                unsafe_allow_html=True
            )
        for item in warning_items[:4]:  # show first 4 warnings
            st.markdown(
                f'<div class="alert-warning">⚠️ <strong>WARNING:</strong> '
                f'{item["display_name"]} is {item["status"]} — '
                f'Value: {item["value"]} {item["unit"]} (Ref: {item["ref_range_str"]})</div>',
                unsafe_allow_html=True
            )
        if len(warning_items) > 4:
            st.caption(f"... and {len(warning_items)-4} more warning(s). See parameter table below.")

    # ── Health Score + Summary Row ─────────────────────────────────────────────
    st.markdown('<div class="section-title">💯 Health Overview</div>', unsafe_allow_html=True)

    hs_data = scores["health_score"]
    col_gauge, col_metrics = st.columns([1, 2])

    with col_gauge:
        # Circular gauge using Plotly
        fig_gauge = go.Figure(go.Indicator(
            mode  = "gauge+number",
            value = hs_data["score"],
            title = {"text": "Health Score", "font": {"size": 14, "color": "#1A5276"}},
            number= {"suffix": "/100", "font": {"size": 28, "color": hs_data["color"]}},
            gauge = {
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#BDC3C7"},
                "bar":  {"color": hs_data["color"], "thickness": 0.35},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  40], "color": "#FADBD8"},
                    {"range": [40, 55], "color": "#FDEBD0"},
                    {"range": [55, 70], "color": "#FEFCE8"},
                    {"range": [70, 85], "color": "#D5F5E3"},
                    {"range": [85,100], "color": "#A9DFBF"},
                ],
                "threshold": {"line": {"color": hs_data["color"], "width": 4}, "value": hs_data["score"]},
            }
        ))
        fig_gauge.update_layout(
            height=250, margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(
            f'<div style="text-align:center; font-weight:600; color:{hs_data["color"]}; font-size:1.1rem;">'
            f'{hs_data["label"]}</div>',
            unsafe_allow_html=True
        )

    with col_metrics:
        # Summary counts
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{counts["total"]}</div>'
                        f'<div class="metric-label">Analyzed</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#1E8449">{counts["normal"]}</div>'
                        f'<div class="metric-label">Normal</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#E67E22">{counts["elevated"]}</div>'
                        f'<div class="metric-label">Elevated</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#2E86C1">{counts["below"]}</div>'
                        f'<div class="metric-label">Below Range</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Risk scores mini-row
        cv_s = scores["cardiovascular"]
        db_s = scores["diabetes"]
        kd_s = scores["kidney"]
        lv_s = scores["liver"]
        tc_s = scores["tc_hdl_ratio"]

        r1, r2, r3, r4, r5 = st.columns(5)
        for col, label, score_d, icon in [
            (r1, "Cardiovascular", cv_s, "🫀"),
            (r2, "Diabetes",       db_s, "🍬"),
            (r3, "Kidney",         kd_s, "🫘"),
            (r4, "Liver",          lv_s, "🫁"),
            (r5, "TC/HDL Ratio",   tc_s, "📊"),
        ]:
            with col:
                if label == "TC/HDL Ratio":
                    val_str = str(score_d.get("ratio", "N/A"))
                    cat_str = score_d.get("category", "N/A")
                    color   = score_d.get("color", "#9E9E9E")
                else:
                    val_str = f"{score_d.get('risk_pct', 0)}%"
                    cat_str = score_d.get("category", "N/A")
                    color   = score_d.get("color", "#9E9E9E")

                st.markdown(
                    f'<div class="risk-card">'
                    f'<div style="font-size:1.4rem">{icon}</div>'
                    f'<div class="risk-name">{label}</div>'
                    f'<div class="risk-pct" style="color:{color}">{val_str}</div>'
                    f'<div class="risk-cat" style="color:{color}">{cat_str}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # ── Charts Section ────────────────────────────────────────────────────────
    if classified:
        st.markdown('<div class="section-title">📈 Visual Summary</div>', unsafe_allow_html=True)
        ch1, ch2 = st.columns([3, 2])

        with ch1:
            # Bar chart — abnormal parameters
            abnormal_items = [c for c in classified if c["status"] != "Normal"][:15]
            if abnormal_items:
                bar_colors = []
                for item in abnormal_items:
                    if item["severity"] == "critical":
                        bar_colors.append("#E74C3C")
                    elif item["status"] in ("High", "Critical High"):
                        bar_colors.append("#E67E22")
                    else:
                        bar_colors.append("#2E86C1")

                # Compute deviation as % of reference max
                deviations = []
                for item in abnormal_items:
                    if item["max_ref"] not in (None, float("inf"), 999):
                        mid = (item["min_ref"] + item["max_ref"]) / 2
                        dev = ((item["value"] - mid) / max(mid, 0.001)) * 100
                    else:
                        dev = 20 if item["status"] in ("High","Critical High") else -20
                    deviations.append(round(dev, 1))

                fig_bar = go.Figure(go.Bar(
                    x     = [c["display_name"] for c in abnormal_items],
                    y     = deviations,
                    marker_color = bar_colors,
                    text  = [f"{c['value']} {c['unit']}" for c in abnormal_items],
                    textposition = "outside",
                    textfont={"size": 9},
                ))
                fig_bar.update_layout(
                    title    = "Parameter Deviation from Reference Midpoint (%)",
                    xaxis    = {"tickangle": -35, "tickfont": {"size": 10}},
                    yaxis    = {"title": "Deviation %", "zeroline": True, "zerolinecolor": "#BDC3C7"},
                    height   = 320,
                    margin   = dict(l=20, r=20, t=50, b=100),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor = "#F8FBFF",
                    showlegend   = False,
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.success("🎉 All parameters are within normal range!")

        with ch2:
            # Pie chart — status distribution
            status_counts = {
                "Normal":        counts["normal"],
                "Elevated/High": counts["elevated"],
                "Below Range":   counts["below"],
            }
            status_counts = {k: v for k, v in status_counts.items() if v > 0}

            if status_counts:
                fig_pie = go.Figure(go.Pie(
                    labels = list(status_counts.keys()),
                    values = list(status_counts.values()),
                    marker_colors = ["#2ECC71", "#E67E22", "#2E86C1"],
                    hole   = 0.45,
                    textinfo = "percent+label",
                    textfont = {"size": 11},
                ))
                fig_pie.update_layout(
                    title  = "Parameter Status Distribution",
                    height = 320,
                    margin = dict(l=10, r=10, t=50, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=True,
                    legend={"font": {"size": 10}},
                )
                st.plotly_chart(fig_pie, use_container_width=True)

    # ── Tabs for Detailed Sections ────────────────────────────────────────────
    st.markdown("")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔬 Parameter Table",
        "🔍 Detected Patterns",
        "⚕️ Disease Risks",
        "🥗 Diet & Lifestyle",
        "💊 Recommendations",
    ])

    with tab1:
        st.markdown("**📋 Parameter Classification Table**")
        if classified:
            df_data = []
            for item in classified:
                status = item["status"]
                if status == "Normal":
                    badge = f'<span class="badge-normal">✅ Normal</span>'
                elif status in ("High", "Critical High"):
                    badge = f'<span class="badge-{"critical" if "Critical" in status else "high"}">' \
                            f'{"🔴 " if "Critical" in status else "⬆️ "}{status}</span>'
                else:
                    badge = f'<span class="badge-{"critical" if "Critical" in status else "low"}">' \
                            f'{"🔴 " if "Critical" in status else "⬇️ "}{status}</span>'

                df_data.append({
                    "Parameter":       item["display_name"],
                    "Category":        item["category"],
                    "Your Value":      f"{item['value']} {item['unit']}",
                    "Reference Range": item["ref_range_str"],
                    "Status":          item["status"],
                    "Deviation %":     f"{item['deviation_pct']}%",
                })

            df = pd.DataFrame(df_data)

            # Color the dataframe rows
            def color_status(val):
                colors_map = {
                    "Normal":        "background-color: #D5F5E3; color: #1E8449",
                    "High":          "background-color: #FDEBD0; color: #E67E22",
                    "Low":           "background-color: #EBF5FB; color: #2E86C1",
                    "Critical High": "background-color: #FADBD8; color: #E74C3C",
                    "Critical Low":  "background-color: #FADBD8; color: #E74C3C",
                }
                return colors_map.get(val, "")

            styled_df = df.style.map(color_status, subset=["Status"])
            st.dataframe(styled_df, use_container_width=True, height=400)
        else:
            st.info("No parameters classified.")

    with tab2:
        st.markdown("**🔍 Detected Clinical Patterns**")
        if patterns:
            for pat in patterns:
                severity = pat.get("severity", "moderate")
                st.markdown(
                    f'<div class="pattern-card {severity}">'
                    f'<div class="pattern-name">{pat["icon"]} {pat["name"]} '
                    f'<span style="font-size:0.75rem; font-weight:400; background:{"#FADBD8" if severity=="high" else "#FDEBD0"}; '
                    f'padding:2px 8px; border-radius:10px;">{severity.upper()}</span></div>'
                    f'<div class="pattern-desc">{pat["description"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                with st.expander(f"Details: {pat['name']}"):
                    st.markdown("**Contributing Factors:**")
                    for c in pat.get("criteria", []):
                        st.markdown(f"• {c}")
                    st.markdown(f"**Advice:** {pat.get('advice', '')}")
                    if pat.get("tc_hdl_ratio"):
                        st.metric("TC/HDL Ratio", pat["tc_hdl_ratio"])
        else:
            st.success("✅ No significant clinical patterns detected.")

    with tab3:
        st.markdown("**⚕️ Disease Risk Predictions**")
        st.caption("Risk estimates based on your blood parameter values. These are NOT diagnoses.")

        if predictions:
            n_cols = min(3, len(predictions))
            pred_cols = st.columns(n_cols)

            for idx, pred in enumerate(predictions):
                with pred_cols[idx % n_cols]:
                    color = pred["color"]
                    st.markdown(
                        f'<div class="risk-card" style="margin-bottom:1rem;">'
                        f'<div style="font-size:2rem">{pred["icon"]}</div>'
                        f'<div class="risk-name">{pred["name"]}</div>'
                        f'<div class="risk-pct" style="color:{color}">{pred["risk_pct"]}%</div>'
                        f'<div class="risk-cat" style="color:{color}">{pred["category"]}</div>'
                        f'<div style="font-size:0.75rem; color:#7F8C8D; margin-top:0.5rem;">'
                        f'{pred["description"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # Risk bar chart
            if predictions:
                fig_risk = go.Figure(go.Bar(
                    x           = [p["risk_pct"] for p in predictions],
                    y           = [f"{p['icon']} {p['name']}" for p in predictions],
                    orientation = "h",
                    marker_color= [p["color"] for p in predictions],
                    text        = [f"{p['risk_pct']}% — {p['category']}" for p in predictions],
                    textposition= "outside",
                ))
                fig_risk.update_layout(
                    title  = "Disease Risk Comparison",
                    xaxis  = {"range": [0, 105], "title": "Estimated Risk %"},
                    height = max(250, len(predictions) * 55),
                    margin = dict(l=20, r=120, t=50, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(248,251,255,1)",
                )
                st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info("Insufficient data for disease risk predictions.")

    with tab4:
        st.markdown("**🥗 Personalized Diet & Lifestyle Recommendations**")

        diet_recs      = recs.get("nutrition", [])
        lifestyle_recs = recs.get("lifestyle", [])

        d_col, l_col = st.columns(2)
        with d_col:
            st.markdown("#### 🍽️ Diet & Nutrition")
            for r in diet_recs:
                st.markdown(
                    f'<div class="rec-item">{r["icon"]} <strong>{r.get("linked","")}:</strong> {r["text"]}</div>',
                    unsafe_allow_html=True
                )

        with l_col:
            st.markdown("#### 🏃 Lifestyle")
            for r in lifestyle_recs:
                st.markdown(
                    f'<div class="rec-item">{r["icon"]} {r["text"]}</div>',
                    unsafe_allow_html=True
                )

    with tab5:
        st.markdown("**💊 Final Recommendations by Category**")

        cat_config = [
            ("cardiovascular", "🫀 Cardiovascular",    "#1A5276"),
            ("nutrition",      "🥗 Nutrition & Diet",  "#1E8449"),
            ("lifestyle",      "🏃 Lifestyle Changes", "#7D6608"),
            ("medical",        "⚕️ Medical Actions",   "#922B21"),
        ]
        for cat_key, cat_label, color in cat_config:
            cat_recs = recs.get(cat_key, [])
            if cat_recs:
                st.markdown(
                    f'<div style="color:{color}; font-weight:600; font-size:1rem; '
                    f'margin:1rem 0 0.5rem 0; padding-bottom:4px; border-bottom:2px solid {color}40;">'
                    f'{cat_label}</div>',
                    unsafe_allow_html=True
                )
                for r in cat_recs:
                    linked_str = f'<span style="color:{color}; font-size:0.78rem;">[{r.get("linked","")}]</span> ' if r.get("linked") else ""
                    st.markdown(
                        f'<div class="rec-item">{r["icon"]} {linked_str}{r["text"]}</div>',
                        unsafe_allow_html=True
                    )

    # ── Download PDF Report ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">📥 Download Your Report</div>', unsafe_allow_html=True)

    dl_col, _ = st.columns([1, 3])
    with dl_col:
        try:
            pdf_bytes = generate_pdf_report(
                parameters      = result["parameters"],
                classified      = classified,
                patterns        = patterns,
                scores          = scores,
                predictions     = predictions,
                recommendations = recs,
                metadata        = meta,
            )
            fname = f"Healytics_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button(
                label     = "⬇️ Download PDF Report",
                data      = pdf_bytes,
                file_name = fname,
                mime      = "application/pdf",
                type      = "primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF generation failed: {e}")
            st.caption("Ensure reportlab is installed: pip install reportlab")

    # ── AI Chatbot Panel ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">🤖 AI Health Assistant</div>', unsafe_allow_html=True)
    st.caption("Ask questions about your blood report, health conditions, or general health advice.")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state["chat_history"]:
            st.markdown(
                '<div class="chat-msg-bot">👋 Hi! I\'m Healytics, your health report assistant. '
                'I can answer questions about your blood test results, explain what different values mean, '
                'or provide general health guidance. What would you like to know?</div>',
                unsafe_allow_html=True
            )
        else:
            for msg in st.session_state["chat_history"]:
                css_class = "chat-msg-user" if msg["role"] == "user" else "chat-msg-bot"
                prefix    = "You: " if msg["role"] == "user" else "Healytics: "
                st.markdown(
                    f'<div class="{css_class}"><strong>{prefix}</strong>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )

    # Quick question buttons
    st.markdown("**Quick Questions:**")
    q_cols = st.columns(4)
    quick_qs = [
        "What does my health score mean?",
        "What should I eat to improve my results?",
        "Explain my cholesterol levels",
        "What are the key risk factors in my report?",
    ]
    for i, q in enumerate(quick_qs):
        with q_cols[i]:
            if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                st.session_state["pending_message"] = q

    # Chat input
    user_input = st.chat_input("Ask a health question...", key="chat_input")
    if "pending_message" in st.session_state:
        user_input = st.session_state.pop("pending_message")

    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        chatbot = st.session_state.get("chatbot") or Chatbot(result)
        response = chatbot.chat(user_input, st.session_state["chat_history"][:-1])
        st.session_state["chat_history"].append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state["chat_history"] = []
        st.rerun()

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="disclaimer">'
        '⚠️ <strong>IMPORTANT DISCLAIMER:</strong> This application is powered by AI and is intended '
        'for <strong>educational and informational purposes only</strong>. It does NOT constitute '
        'medical advice, diagnosis, or treatment. The analysis and recommendations provided should '
        'NOT be used as a substitute for professional medical consultation. Always consult a '
        'qualified healthcare professional (doctor, specialist) for interpretation of your test '
        'results, diagnosis, and treatment decisions. Do not disregard professional medical advice '
        'or delay seeking it based on this AI-generated report.'
        '</div>',
        unsafe_allow_html=True
    )

    # Reset button
    st.markdown("<br>", unsafe_allow_html=True)
    col_reset, _ = st.columns([1, 3])
    with col_reset:
        if st.button("🔄 Analyze New Report", use_container_width=True):
            st.session_state["analysis_done"]   = False
            st.session_state["analysis_result"] = None
            st.session_state["chat_history"]    = []
            st.session_state["chatbot"]         = None
            st.rerun()

# ── Empty State ───────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding:3rem 1rem; color:#5D6D7E;">
        <div style="font-size:4rem; margin-bottom:1rem;">🔬</div>
        <h3 style="color:#1A5276;">Ready to Analyze Your Blood Report</h3>
        <p style="font-size:0.95rem; max-width:500px; margin:0 auto; line-height:1.7;">
            Choose an input method above, upload or enter your blood report data, 
            and click <strong>Analyze</strong> to get AI-powered insights, 
            risk predictions, and personalized health recommendations.
        </p>
        <br>
        <div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; font-size:0.85rem;">
            <span>✅ Parameter Classification</span>
            <span>🔍 Pattern Detection</span>
            <span>⚕️ Disease Risk Scoring</span>
            <span>💊 Personalized Advice</span>
            <span>📥 PDF Report Download</span>
            <span>🤖 AI Health Chatbot</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick-start tip
    st.markdown(
        '<div class="alert-info" style="max-width:600px; margin:1rem auto;">💡 <strong>Quick Start:</strong> '
        'Click any sample report button in the left sidebar to see a full demo analysis instantly!</div>',
        unsafe_allow_html=True
    )