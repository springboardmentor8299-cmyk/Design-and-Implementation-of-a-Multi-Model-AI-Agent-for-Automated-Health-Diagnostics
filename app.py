import streamlit as st
import pytesseract
from PIL import Image
import re
import pandas as pd
import fitz  # PyMuPDF

# Uncomment if needed:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
st.set_page_config(page_title="Blood Report Analyzer")
st.title("Blood Report Analysis System")
st.write("Upload PDF or Image to extract and analyze blood report values.")

uploaded_file = st.file_uploader(
    "Upload Blood Report (PDF / JPG / PNG)",
    type=["pdf", "jpg", "jpeg", "png"]
)

# ----------------------------
# Extract text from PDF (Memory-based, no temp files)
# ----------------------------

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text += page_text + "\n"

        # If no text → apply OCR
        if not text.strip():
            for page in doc:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img)

        doc.close()

    except Exception as e:
        st.error(f"Error processing PDF: {e}")

    return text

# ----------------------------
# Extract text from image
# ----------------------------

def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file)
    return pytesseract.image_to_string(image)

# ----------------------------
# Extract parameters
# ----------------------------

def extract_parameters(text):
    extracted = []

    patterns = {
        "Hemoglobin": r"Hemoglobin[:\s]+([\d\.]+)",
        "Glucose": r"Glucose[:\s]+([\d\.]+)",
        "Cholesterol": r"Cholesterol[:\s]+([\d\.]+)",
        "Blood Percentage": r"Blood Percentage[:\s]+([\d\.]+)",
        "HbA1c": r"(HbA1c|Blood Sugar Percentage).*?([\d\.]+)"
    }

    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.groups()[-1])
            extracted.append([param, value])

    return pd.DataFrame(extracted, columns=["Parameter", "Value"])

# ----------------------------
# Prediction + Accuracy + Diabetes Logic
# ----------------------------

def predict_status_and_accuracy(parameter, value):

    ranges = {
        "Hemoglobin": (12, 16),
        "Glucose": (70, 110),
        "Cholesterol": (125, 200),
        "Blood Percentage": (40, 50),   # Example normal %
        "HbA1c": (4, 5.6)
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

# ----------------------------
# Diabetes Detection
# ----------------------------

def detect_diabetes(df):
    diabetes_status = "No Diabetes Detected"

    for _, row in df.iterrows():
        if row["Parameter"] == "Glucose" and row["Value"] > 126:
            diabetes_status = "Diabetes Likely"
        if row["Parameter"] == "HbA1c" and row["Value"] >= 6.5:
            diabetes_status = "Diabetes Likely"

    return diabetes_status

# ----------------------------
# MAIN
# ----------------------------

if uploaded_file is not None:

    st.success("File uploaded successfully!")

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

            # Diabetes Check
            diabetes_result = detect_diabetes(extracted_df)

            st.subheader("Diabetes Evaluation")
            st.write(diabetes_result)

            st.download_button(
                label="Download Result CSV",
                data=extracted_df.to_csv(index=False),
                file_name="blood_report_analysis.csv",
                mime="text/csv"
            )
