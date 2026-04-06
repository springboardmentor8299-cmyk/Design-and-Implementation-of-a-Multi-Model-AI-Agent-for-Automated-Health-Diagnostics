import os
import re
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import cv2
import numpy as np


# 🔴 SET TESSERACT PATH (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# 🧼 PREPROCESS
def preprocess(img):
    img = np.array(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    return gray


# 🔍 TEXT EXTRACTION (NO POPPLER)
def extract_text(filepath):

    if not os.path.exists(filepath):
        print("❌ File not found")
        return ""

    text = ""

    try:
        # 📄 PDF HANDLING (PyMuPDF)
        if filepath.lower().endswith(".pdf"):

            doc = fitz.open(filepath)

            print(f"📄 Pages: {len(doc)}")

            for i, page in enumerate(doc):

                # 1️⃣ Try direct text
                page_text = page.get_text()

                if page_text.strip():
                    print(f"\n--- Page {i+1} TEXT ---")
                    print(page_text[:300])
                    text += page_text + "\n"

                else:
                    # 2️⃣ OCR fallback (scanned PDF)
                    print(f"🔍 OCR on page {i+1}")

                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    processed = preprocess(img)

                    ocr_text = pytesseract.image_to_string(processed)

                    print(f"--- Page {i+1} OCR ---")
                    print(ocr_text[:300])

                    text += ocr_text + "\n"

        # 🖼 IMAGE
        else:
            img = Image.open(filepath)
            processed = preprocess(img)

            text = pytesseract.image_to_string(processed)

            print("\n--- Image OCR ---")
            print(text[:300])

    except Exception as e:
        print("❌ Extraction Error:", e)

    # 🔧 CLEANUP (OCR errors)
    text = text.replace("Hernoglobin", "Hemoglobin")
    text = text.replace("Glocose", "Glucose")

    return text


# 🧪 PARAMETER EXTRACTION
def extract_parameters(text):

    data = {}

    if not text.strip():
        print("❌ No text extracted")
        return data

    print("\n🔍 Extracting parameters...\n")

    patterns = {
        "Hemoglobin": r"(Hemoglobin|Hb)[^\d]{0,20}(\d+\.?\d*)",
        "Glucose": r"(Glucose|Blood Sugar)[^\d]{0,20}(\d+\.?\d*)",
        "Cholesterol": r"(Cholesterol)[^\d]{0,20}(\d+\.?\d*)",
        "WBC": r"(WBC|White Blood Cells)[^\d]{0,20}(\d+)",
        "RBC": r"(RBC|Red Blood Cells)[^\d]{0,20}(\d+\.?\d*)",
        "Platelet": r"(Platelet|Platelets)[^\d]{0,20}(\d+)",
        "Creatinine": r"(Creatinine)[^\d]{0,20}(\d+\.?\d*)",
        "Urea": r"(Urea)[^\d]{0,20}(\d+\.?\d*)"
    }

    for param, pattern in patterns.items():

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.groups()[-1]
            data[param] = float(value)
            print(f"✅ {param}: {value}")
        else:
            print(f"❌ {param} not found")

    return data