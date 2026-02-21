import streamlit as st
import pdfplumber
import pandas as pd
import json
import google.generativeai as genai

# --- CONFIGURATION ---
# Replace with your actual Gemini API Key
GEMINI_API_KEY = "AIzaSyByQi0cGPVEc3iEtv4FqktxWIy7YSRV3lw"

# 1. Standard Reference Ranges (Hematology & Biochemistry)
BLOOD_STANDARDS = {
    "Glucose": {"min": 70, "max": 99, "unit": "mg/dL"},
    "Cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
    "Hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
    "WBC Count": {"min": 4.5, "max": 11.0, "unit": "x10^3/uL"},
    "RBC Count": {"min": 4.5, "max": 5.9, "unit": "million/uL"},
    "Platelets": {"min": 150, "max": 450, "unit": "x10^3/uL"},
    "Albumin": {"min": 3.4, "max": 5.4, "unit": "g/dL"},
    "Creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL"}
}


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
    3. Standardize names to: Glucose, Cholesterol, Hemoglobin, WBC Count, RBC Count, Platelets, Albumin, Creatinine.

    Return JSON:
    {{
      "is_blood_report": true/false,
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


def build_comparative_table(extracted_data):
    report_data = []

    for item in extracted_data:
        test_name = item.get("Test")
        current_val = item.get("Value")
        unit = item.get("Unit")

        # Get standard reference
        ref = BLOOD_STANDARDS.get(test_name)

        if ref:
            standard_range = f"{ref['min']} - {ref['max']} {ref['unit']}"

            # Comparison Logic
            if current_val < ref['min']:
                status = "🔴 LOW"
            elif current_val > ref['max']:
                status = "🔴 HIGH"
            else:
                status = "🟢 NORMAL"

            report_data.append({
                "Test Name": test_name,
                "Your Value": f"{current_val} {unit}",
                "Standard Range": standard_range,
                "Status": status
            })

    return pd.DataFrame(report_data)


# --- UI INTERFACE ---
st.set_page_config(page_title="Blood Lab AI", layout="wide")

st.title("💉Blood Report Comparative Analysis")
st.write("Upload your PDF report to compare your results against standard medical ranges.")
st.divider()
st.image("Agent.jpg")

uploaded_file = st.file_uploader("Choose a Blood Report PDF", type="pdf")

if uploaded_file:
    with st.spinner("Extracting and comparing data..."):
        # PDF Extraction
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        if text.strip():
            data = ai_blood_extraction(text)

            if data.get("is_blood_report") and data.get("results"):
                df = build_comparative_table(data["results"])

                if not df.empty:
                    st.subheader("Comparison Table")
                    # Displaying the clean table
                    st.table(df)

                    st.info(
                        "Note: This analysis is for informational purposes only. Consult a doctor for medical advice.")
                else:
                    st.warning("No matching standard blood markers found.")
            else:
                st.error("Document not recognized as a blood report or no data found.")
        else:
            st.error("Could not read text from PDF.")