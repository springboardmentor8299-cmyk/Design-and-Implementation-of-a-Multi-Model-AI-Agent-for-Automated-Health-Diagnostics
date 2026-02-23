import streamlit as st
import fitz
import pytesseract
from PIL import Image
import io
import pandas as pd
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="AI Health Diagnostic Agent", layout="wide")
st.title("AI Health Diagnostic Agent")

uploaded_file = st.file_uploader("Upload Blood Report (PDF)", type=["pdf"])

def extract_content(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        text = page.get_text()
        if text.strip(): full_text += text
        else:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes())).convert('L')
            full_text += pytesseract.image_to_string(img)
    return full_text

TESTS = {
    "Hemoglobin": {"aliases": ["Hemoglobin", "Hb"], "low": 13.0, "high": 17.0, "unit": "g/dL"},
    "Glucose": {"aliases": ["Glucose", "FBS", "Sugar"], "normal": 100, "medium": 125, "unit": "mg/dL"},
    "Cholesterol": {"aliases": ["Cholesterol", "Total Cholesterol"], "normal": 200, "medium": 239, "unit": "mg/dL"},
    "Creatinine": {"aliases": ["Creatinine", "CREA"], "low": 0.7, "high": 1.3, "unit": "mg/dL"},
    "Platelets": {"aliases": ["Platelets", "PLT", "Platelet Count"], "low": 150, "high": 450, "unit": "10^3/µL"},
    "WBC Count": {"aliases": ["Total Leucocyte Count", "WBC", "TLC"], "low": 4.0, "high": 11.0, "unit": "10^3/µL"}
}

def interpret_value(test_name, val):
    ref = TESTS[test_name]
    if "medium" in ref:
        if val <= ref["normal"]: return "Normal"
        elif val <= ref["medium"]: return "Medium (Borderline)"
        else: return "High (Critical)"
    else:
        if val < ref["low"]: return "Low"
        if val > ref["high"]: return "High"
        return "Normal"

if uploaded_file:
    with st.spinner("Analyzing..."):
        raw_text = extract_content(uploaded_file.read())
        results = []
        for test_name, info in TESTS.items():
            for alias in info["aliases"]:
                pattern = rf"{alias}.*?(\d+\.?\d*)"
                match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
                if match:
                    val = float(match.group(1))
                    if test_name == "WBC Count" and val > 100: val = val / 1000
                    results.append({
                        "Parameter": test_name, 
                        "Value": val, 
                        "Unit": info["unit"], 
                        "Status": interpret_value(test_name, val)
                    })
                    break

        if results:
            st.subheader("Diagnostic Summary")
            df = pd.DataFrame(results)
            df['Value'] = df['Value'].apply(lambda x: f"{x:.2f}")
            def style_status(val):
                if "High" in val or "Low" in val: color = '#ffcccc' 
                elif "Medium" in val: color = '#ffffcc' 
                else: color = '#ccffcc'
                return f'background-color: {color}'
            st.table(df.style.applymap(style_status, subset=['Status']))