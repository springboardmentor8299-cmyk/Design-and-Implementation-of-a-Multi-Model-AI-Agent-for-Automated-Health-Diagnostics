import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd
import fitz  # PyMuPDF
from risk import detect_health_risks, generate_health_recommendations


# Tesseract path (change if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="Blood Report Analyzer")

st.title("Blood Report Analysis System")
st.write("Upload PDF or Image to extract and analyze blood report values.")
# --------------------------------------------------
# Patient Details Input
# --------------------------------------------------

st.subheader("Patient Details")

col1, col2 = st.columns(2)

with col1:
    patient_age = st.number_input("Enter Age", min_value=0, max_value=120, step=1)

with col2:
    patient_gender = st.selectbox("Select Gender", ["Male", "Female", "Other"])


uploaded_file = st.file_uploader(
    "Upload Blood Report (PDF / JPG / PNG)",
    type=["pdf", "jpg", "jpeg", "png"]
)

# --------------------------------------------------
# Extract text from PDF
# --------------------------------------------------

def extract_text_from_pdf(uploaded_file):

    text = ""

    try:
        file_bytes = uploaded_file.read()

        doc = fitz.open(stream=file_bytes, filetype="pdf")

        for page in doc:

            page_text = page.get_text()

            if page_text.strip():
                text += page_text + "\n"

        # If PDF has no selectable text → use OCR
        if not text.strip():

            for page in doc:

                pix = page.get_pixmap()

                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                text += pytesseract.image_to_string(img)

        doc.close()

    except Exception as e:
        st.error(f"Error processing PDF: {e}")

    return text


# --------------------------------------------------
# Extract text from image
# --------------------------------------------------

def extract_text_from_image(uploaded_file):

    image = Image.open(uploaded_file)

    text = pytesseract.image_to_string(image)

    return text


# --------------------------------------------------
# Extract parameters (9 parameters)
# --------------------------------------------------

def extract_parameters(text):

    extracted = []

    patterns = {

        "Hemoglobin": r"Hemoglobin[:\s]+([\d\.]+)",
        "Glucose": r"Glucose[:\s]+([\d\.]+)",
        "Cholesterol": r"Cholesterol[:\s]+([\d\.]+)",
        "Blood Percentage": r"Blood Percentage[:\s]+([\d\.]+)",
        "HbA1c": r"(HbA1c|Blood Sugar Percentage).*?([\d\.]+)",
        "WBC": r"(WBC|White Blood Cells)[:\s]+([\d\.]+)",
        "RBC": r"(RBC|Red Blood Cells)[:\s]+([\d\.]+)",
        "Platelets": r"(Platelets|Platelet Count)[:\s]+([\d\.]+)",
        "Triglycerides": r"Triglycerides[:\s]+([\d\.]+)"

    }

    for param, pattern in patterns.items():

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            value = float(match.groups()[-1])

            extracted.append([param, value])

    df = pd.DataFrame(extracted, columns=["Parameter", "Value"])

    return df


# --------------------------------------------------
# Prediction (Normal / Low / High)
# --------------------------------------------------

def predict_status_and_accuracy(parameter, value):

    ranges = {

        "Hemoglobin": (12, 16),
        "Glucose": (70, 110),
        "Cholesterol": (125, 200),
        "Blood Percentage": (40, 50),
        "HbA1c": (4, 5.6),
        "WBC": (4000, 11000),
        "RBC": (4.5, 5.9),
        "Platelets": (150000, 450000),
        "Triglycerides": (0, 150)

    }

    if parameter not in ranges:

        return "Unknown", "N/A"

    low, high = ranges[parameter]

    if low <= value <= high:

        status = "Normal"
        accuracy = 95

    elif value < low:

        status = "Low"
        accuracy = min(99, 80 + (low - value) * 2)

    else:

        status = "High"
        accuracy = min(99, 80 + (value - high) * 2)

    return status, f"{int(accuracy)}%"


# --------------------------------------------------
# Diabetes detection
# --------------------------------------------------

def detect_diabetes(df):

    diabetes_status = "No Diabetes Detected"

    for _, row in df.iterrows():

        if row["Parameter"] == "Glucose" and row["Value"] > 126:

            diabetes_status = "Diabetes Likely"

        if row["Parameter"] == "HbA1c" and row["Value"] >= 6.5:

            diabetes_status = "Diabetes Likely"

    return diabetes_status



# --------------------------------------------------
# MAIN
# --------------------------------------------------

if uploaded_file is not None:

    st.success("File uploaded successfully!")
    # Show patient info
    st.subheader("Patient Information")
    st.write(f"Age: {patient_age}")
    st.write(f"Gender: {patient_gender}")


    if uploaded_file.type == "application/pdf":

        text = extract_text_from_pdf(uploaded_file)

    else:

        text = extract_text_from_image(uploaded_file)

    if not text.strip():

        st.error("Could not extract text. The file may be unreadable.")

    else:

        st.subheader("Extracted Text Preview")

        st.text(text[:500])

        extracted_df = extract_parameters(text)

        if extracted_df.empty:

            st.warning("No blood parameters detected.")

        else:

            predictions = []
            accuracies = []

            for _, row in extracted_df.iterrows():

                status, accuracy = predict_status_and_accuracy(
                    row["Parameter"], row["Value"]
                )

                predictions.append(status)
                accuracies.append(accuracy)

            extracted_df["Prediction"] = predictions
            extracted_df["Accuracy (%)"] = accuracies

            st.subheader("Blood Report Analysis Result")

            st.dataframe(extracted_df)

            # Diabetes evaluation
            diabetes_result = detect_diabetes(extracted_df)

            st.subheader("Diabetes Evaluation")

            st.write(diabetes_result)
            st.subheader("Health Risk Analysis")

            risks = detect_health_risks(extracted_df)

            for r in risks:
                st.warning(r)

            # --------------------------------------------------
            # Health Recommendations
            # --------------------------------------------------

            st.subheader("Health Recommendations")

            recommendations = generate_health_recommendations(risks)

            for rec in recommendations:
                st.info(rec)

            # Download option
            st.download_button(
                label="Download Result CSV",
                data=extracted_df.to_csv(index=False),
                file_name="blood_report_analysis.csv",
                mime="text/csv"
            )
