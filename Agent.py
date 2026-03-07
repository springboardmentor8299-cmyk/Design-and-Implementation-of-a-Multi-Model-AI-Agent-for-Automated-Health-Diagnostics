import streamlit as st
import pdfplumber
import pandas as pd
import json
import google.generativeai as genai
import plotly.graph_objects as go
import pytesseract
from PIL import Image
import io

try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    pass

GEMINI_API_KEY = "AIzaSyB25EZBc8HBbfE_XibiILsPpvUgvsQMmDc"  

BLOOD_STANDARDS = {
    "Glucose": {"min": 70, "max": 99, "unit": "mg/dL", "critical_low": 50, "critical_high": 200},
    "Cholesterol": {"min": 0, "max": 200, "unit": "mg/dL", "critical_low": 0, "critical_high": 300},
    "Hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL", "critical_low": 7, "critical_high": 20},
    "WBC Count": {"min": 4.5, "max": 11.0, "unit": "x10^3/uL", "critical_low": 2, "critical_high": 30},
    "RBC Count": {"min": 4.5, "max": 5.9, "unit": "million/uL", "critical_low": 3, "critical_high": 7},
    "Platelets": {"min": 150, "max": 450, "unit": "x10^3/uL", "critical_low": 50, "critical_high": 1000},
    "Albumin": {"min": 3.4, "max": 5.4, "unit": "g/dL", "critical_low": 2, "critical_high": 6},
    "Creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL", "critical_low": 0.3, "critical_high": 5},
    "HDL": {"min": 40, "max": 999, "unit": "mg/dL", "critical_low": 20, "critical_high": 999},
    "LDL": {"min": 0, "max": 100, "unit": "mg/dL", "critical_low": 0, "critical_high": 190},
    "Triglycerides": {"min": 0, "max": 150, "unit": "mg/dL", "critical_low": 0, "critical_high": 500}
}

UNIT_CONVERSIONS = {
    "Glucose": {"mmol/L": 18.0182},
    "Cholesterol": {"mmol/L": 38.67},
    "Hemoglobin": {"mmol/L": 0.06206}
}

def parse_input(uploaded_file, file_type, use_ocr=False):
    if file_type == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        return {"type": "text", "content": text}
    elif file_type == "json":
        data = json.load(uploaded_file)
        return {"type": "json", "content": data}
    elif file_type in ["png", "jpg", "jpeg"] and use_ocr:
        try:
            img = Image.open(uploaded_file)
            text = pytesseract.image_to_string(img)
            return {"type": "text", "content": text}
        except Exception as e:
            st.error(f"OCR Error: Tesseract not installed. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            return None
    return None

def ai_blood_extraction(text):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = f"""
    You are a Hematology Extraction Expert. 
    Task:
    1. Verify if the text belongs to a Blood Test Report.
    2. Extract test names and their numeric values. 
    3. Standardize names to: Glucose, Cholesterol, Hemoglobin, WBC Count, RBC Count, Platelets, Albumin, Creatinine, HDL, LDL, Triglycerides.
    4. Extract patient info if available: name, age, gender, date.

    Return JSON:
    {{
      "is_blood_report": true/false,
      "patient_info": {{"name": "string", "age": number, "gender": "string", "date": "string"}},
      "results": [
        {{"Test": "string", "Value": numeric, "Unit": "string"}}
      ]
    }}

    Text: {text}
    """

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        st.error(f"API Error: {e}")
        return {"is_blood_report": False, "results": []}

def validate_and_standardize(data):
    standardized = []
    for item in data:
        test = item.get("Test")
        value = item.get("Value")
        unit = item.get("Unit", "")
        
        if test in UNIT_CONVERSIONS and unit in UNIT_CONVERSIONS[test]:
            value = value * UNIT_CONVERSIONS[test][unit]
            unit = BLOOD_STANDARDS[test]["unit"]
        
        if isinstance(value, (int, float)) and value >= 0:
            standardized.append({"Test": test, "Value": value, "Unit": unit})
    
    return standardized

def interpret_parameter(test_name, value, ref, age=None, gender=None):
    if test_name == "Hemoglobin" and gender:
        if gender == "Male":
            ref = {**ref, "min": 13.5, "max": 17.5}
        elif gender == "Female":
            ref = {**ref, "min": 12.0, "max": 15.5}
    
    if test_name == "Glucose" and age and age > 60:
        ref = {**ref, "max": 110}
    
    if value < ref['min']:
        if value < ref.get('critical_low', ref['min']):
            return "Critical Low", "🔴", "#ff0000"
        return "Low", "🟡", "#ffa500"
    elif value > ref['max']:
        if value > ref.get('critical_high', ref['max']):
            return "Critical High", "🔴", "#ff0000"
        return "High", "🟡", "#ffa500"
    return "Normal", "🟢", "#00ff00"

def build_comparative_table(extracted_data, age=None, gender=None):
    report_data = []
    chart_data = []

    for item in extracted_data:
        test_name = item.get("Test")
        current_val = item.get("Value")
        unit = item.get("Unit")
        ref = BLOOD_STANDARDS.get(test_name)

        if ref:
            standard_range = f"{ref['min']} - {ref['max']} {ref['unit']}"
            status_text, emoji, color = interpret_parameter(test_name, current_val, ref, age, gender)

            report_data.append({
                "Test Name": test_name,
                "Your Value": f"{current_val} {unit}",
                "Standard Range": standard_range,
                "Status": f"{emoji} {status_text}"
            })
            
            chart_data.append({
                "Test": test_name,
                "Value": current_val,
                "Min": ref['min'],
                "Max": ref['max'],
                "Status": status_text,
                "Color": color
            })

    return pd.DataFrame(report_data), chart_data

def create_bar_chart(chart_data):
    fig = go.Figure()
    
    for item in chart_data:
        color = '#00ff00' if item['Status'] == 'Normal' else '#ff0000' if 'Critical' in item['Status'] else '#ffa500'
        
        fig.add_trace(go.Bar(
            y=[item['Test']],
            x=[item['Value']],
            name=item['Test'],
            orientation='h',
            marker=dict(color=color),
            text=[f"{item['Value']}"],
            textposition='auto',
        ))
        
        fig.add_shape(type="line",
            x0=item['Min'], y0=item['Test'], x1=item['Min'], y1=item['Test'],
            line=dict(color="green", width=3, dash="dash"))
        fig.add_shape(type="line",
            x0=item['Max'], y0=item['Test'], x1=item['Max'], y1=item['Test'],
            line=dict(color="red", width=3, dash="dash"))
    
    fig.update_layout(
        title="Parameter Values vs Reference Ranges",
        xaxis_title="Value",
        yaxis_title="Test Parameter",
        showlegend=False,
        height=400,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

def calculate_risk_scores(data_dict, age, gender):
    risks = {"patterns": [], "scores": {}}
    
    glucose = data_dict.get("Glucose", 0)
    cholesterol = data_dict.get("Cholesterol", 0)
    hdl = data_dict.get("HDL", 0)
    ldl = data_dict.get("LDL", 0)
    triglycerides = data_dict.get("Triglycerides", 0)
    
    metabolic_indicators = 0
    if glucose >= 100: metabolic_indicators += 1
    if triglycerides >= 150: metabolic_indicators += 1
    if hdl < 40: metabolic_indicators += 1
    
    if metabolic_indicators >= 2:
        risks["patterns"].append({
            "name": "Metabolic Syndrome Risk",
            "severity": "High" if metabolic_indicators == 3 else "Moderate"
        })
    
    cv_risk_score = 0
    if age > 45: cv_risk_score += 2
    if gender == "Male": cv_risk_score += 1
    if cholesterol > 200: cv_risk_score += 2
    if ldl > 130: cv_risk_score += 2
    if hdl < 40: cv_risk_score += 1
    if triglycerides > 150: cv_risk_score += 1
    
    risks["scores"]["Cardiovascular Risk"] = {
        "level": "High" if cv_risk_score >= 6 else "Moderate" if cv_risk_score >= 3 else "Low",
        "percentage": min(cv_risk_score * 10, 100)
    }
    
    if cholesterol > 0 and hdl > 0:
        tc_hdl_ratio = cholesterol / hdl
        risks["scores"]["TC/HDL Ratio"] = {
            "value": round(tc_hdl_ratio, 2),
            "level": "High" if tc_hdl_ratio > 5 else "Moderate" if tc_hdl_ratio > 3.5 else "Optimal"
        }
    
    if glucose >= 126:
        risks["patterns"].append({"name": "Diabetes Indicator", "severity": "High"})
    elif glucose >= 100:
        risks["patterns"].append({"name": "Pre-Diabetes Indicator", "severity": "Moderate"})
    
    return risks

st.set_page_config(page_title="AI Health Diagnostics", layout="wide", page_icon="🏥")

st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    h1 {color: #2c3e50; text-align: center; font-size: 3em;}
</style>
""", unsafe_allow_html=True)

st.title("🏥 AI Health Diagnostic System")
st.markdown("### Multi-Model Blood Report Analysis Platform")

with st.sidebar:
    st.header("⚙️ Settings")
    st.subheader("👤 Patient Details")
    patient_age = st.number_input("Age", min_value=1, max_value=120, value=30)
    patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    st.divider()
    st.subheader("🔍 OCR Settings")
    use_ocr = st.checkbox("Enable OCR for Images", value=False)
    st.divider()
    st.info("Upload PDF, JSON, or Image formats")

uploaded_file = st.file_uploader("📄 Upload Blood Report", type=["pdf", "json", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    with st.spinner("🔄 Processing report..."):
        parsed_data = parse_input(uploaded_file, file_type, use_ocr)
        
        if parsed_data and parsed_data["type"] == "text":
            text = parsed_data["content"]
            
            if text.strip():
                data = ai_blood_extraction(text)

                if data.get("is_blood_report") and data.get("results"):
                    validated_data = validate_and_standardize(data["results"])
                    
                    st.markdown("### 👤 Patient Information")
                    cols = st.columns(4)
                    cols[0].metric("Age", patient_age)
                    cols[1].metric("Gender", patient_gender)
                    if data.get("patient_info"):
                        info = data["patient_info"]
                        if info.get("name"): cols[2].metric("Name", info["name"])
                        if info.get("date"): cols[3].metric("Date", info["date"])
                    st.divider()
                    
                    df, chart_data = build_comparative_table(validated_data, patient_age, patient_gender)

                    if not df.empty:
                        data_dict = {item["Test"]: item["Value"] for item in validated_data}
                        risk_analysis = calculate_risk_scores(data_dict, patient_age, patient_gender)
                        
                        st.markdown("### 📊 Analysis Summary")
                        col1, col2, col3 = st.columns(3)
                        normal = df[df['Status'].str.contains('Normal')].shape[0]
                        abnormal = df.shape[0] - normal
                        col1.metric("Total Tests", df.shape[0])
                        col2.metric("Normal", normal, delta="Good")
                        col3.metric("Abnormal", abnormal, delta="Review")
                        
                        if risk_analysis["scores"]:
                            st.divider()
                            st.markdown("### ⚠️ Risk Assessment (Model 2)")
                            risk_cols = st.columns(len(risk_analysis["scores"]))
                            for idx, (risk_name, risk_data) in enumerate(risk_analysis["scores"].items()):
                                with risk_cols[idx]:
                                    if "percentage" in risk_data:
                                        st.metric(risk_name, f"{risk_data['percentage']}%", delta=risk_data['level'])
                                    else:
                                        st.metric(risk_name, risk_data['value'], delta=risk_data['level'])
                        
                        if risk_analysis["patterns"]:
                            st.divider()
                            st.markdown("### 🔍 Pattern Recognition (Model 2)")
                            for pattern in risk_analysis["patterns"]:
                                severity_color = "🔴" if pattern["severity"] == "High" else "🟡"
                                st.warning(f"{severity_color} **{pattern['name']}** - Severity: {pattern['severity']}")
                        
                        st.divider()
                        st.markdown("### 📋 Detailed Results")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        st.divider()
                        st.markdown("### 📊 Visual Comparison")
                        fig = create_bar_chart(chart_data)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.success("✅ Analysis Complete! Models 1, 2, and 3 Integrated")
                        st.info("⚠️ This analysis is for informational purposes only. Consult a healthcare professional.")
                    else:
                        st.warning("⚠️ No matching standard blood markers found.")
                else:
                    st.error("❌ Document not recognized as a blood report.")
            else:
                st.error("❌ Could not read text from file.")

st.divider()
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>🏥 AI Health Diagnostic System | Powered by Google Gemini AI</p>
    <p>Model 1: Parameter Interpretation | Model 2: Risk Assessment | Model 3: Contextual Analysis</p>
</div>
""", unsafe_allow_html=True)
