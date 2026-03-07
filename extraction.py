# extraction.py
import pdfplumber
import re

def extract_text_from_pdf(pdf_file):
    """Extract all text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_parameters(text):
    """Extract blood parameters from text using regex."""
    # Patterns for each parameter (adjust as needed)
    patterns = {
        "Hemoglobin": r"Hemoglobin\s*:?\s*([\d\.]+)",
        "WBC": r"WBC|White Blood Cells?\s*:?\s*([\d,]+)",
        "Platelets": r"Platelets?\s*:?\s*([\d,]+)",
        "Glucose": r"Glucose|Blood Sugar\s*:?\s*([\d\.]+)",
        "Cholesterol": r"Cholesterol\s*:?\s*([\d\.]+)",
        "HDL": r"HDL\s*:?\s*([\d\.]+)",
    }
    
    extracted = {}
    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(',', '')  # remove commas
            try:
                extracted[param] = float(value_str)
            except ValueError:
                extracted[param] = None  # if conversion fails
        else:
            extracted[param] = None
    return extracted