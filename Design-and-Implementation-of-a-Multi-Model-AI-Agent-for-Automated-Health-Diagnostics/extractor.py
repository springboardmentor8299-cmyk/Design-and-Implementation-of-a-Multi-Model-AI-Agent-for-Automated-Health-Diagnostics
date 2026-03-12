from importlib.resources import path
import numbers
import os
import re
import csv
import pdfplumber
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
from PIL import ImageEnhance, ImageFilter

# =========================================================
# TESSERACT PATH (CHANGE IF NEEDED)
# =========================================================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================================================
# KNOWN PARAMETERS
# =========================================================
KNOWN_PARAMETERS = {
    "patient_name",
    "age",
    "gender",

    "fasting_plasma_glucose",
    "post_prandial_plasma_glucose",
    "hba1c",

    "total_cholesterol",
    "hdl_cholesterol",
    "ldl_cholesterol",
    "triglycerides",

    "tsh",
    "t3",
    "t4",

    "bilirubin_total",
    "sgot",
    "sgpt",
    "alp",

    "urea",
    "creatinine",

    "hemoglobin",
    "wbc_count",
    "platelet_count"
}


# =========================================================
# PARAMETER NAME ALIASES
# =========================================================
PARAMETER_ALIASES = {
    "hemoglobin": ["hemoglobin", "haemoglobin"],
    "wbc_count": ["wbc", "total leukocyte count"],
    "platelet_count": ["platelet"],
    "fasting_plasma_glucose": ["fasting plasma glucose", "fpg"],
    "post_prandial_plasma_glucose": ["post prandial plasma glucose", "ppg"],
    "hba1c": ["hba1c"],
    "total_cholesterol": ["total cholesterol"],
    "hdl_cholesterol": ["hdl cholesterol"],
    "ldl_cholesterol": ["ldl cholesterol"],
    "triglycerides": ["triglycerides"],
    "tsh": ["tsh"],
    "t3": ["t3"],
    "t4": ["t4"],
    "bilirubin_total": ["bilirubin total"],
    "sgot": ["sgot", "ast"],
    "sgpt": ["sgpt", "alt"],
    "alp": ["alkaline phosphatase", "alp"],
    "urea": ["urea"],
    "creatinine": ["creatinine"],
}


# =========================================================
# TEXT EXTRACTION FROM FILE
# =========================================================
def extract_text(path: str) -> str:

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    text_out = []

    # ---------------- IMAGE ----------------
    if ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        img = Image.open(path)
        text_out.append(pytesseract.image_to_string(img))

    # ---------------- PDF ------------------
    elif ext == ".pdf":

        with pdfplumber.open(path) as pdf:

            is_text_pdf = False

            # detect text PDF
            for page in pdf.pages[:2]:
                t = page.extract_text()
                if t and len(t.strip()) > 20:
                    is_text_pdf = True
                    break

            # TEXT PDF
            if is_text_pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_out.append(t)
                    else:
                        img = page.to_image(resolution=300).original
                        text_out.append(pytesseract.image_to_string(img))

            # SCANNED PDF
            else:
                images = convert_from_path(path, dpi=300)
                for img in images:
                    text_out.append(pytesseract.image_to_string(img))

    # ---------------- TEXT FILE ----------------
    elif ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            text_out.append(f.read())

    else:
        raise ValueError("Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP, TXT")

    return normalize_text("\n".join(text_out))


# =========================================================
# TEXT CLEANING
# =========================================================
def normalize_text(text: str) -> str:
    text = text.lower()

    text = text.translate(str.maketrans({
        "–": "-",
        "—": "-",
        "−": "-",
        "×": "x",
        "X": "x"
    }))

    text = re.sub(r"[^\x00-\x7f]", " ", text)
    text = re.sub(r"\.{2,}", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)

    return text.strip()


# =========================================================
# PARAMETER EXTRACTION
# =========================================================
def extract_parameters(text: str) -> dict:

    extracted = {p: None for p in KNOWN_PARAMETERS}

    lines = text.splitlines()

    for line in lines:
        for param, aliases in PARAMETER_ALIASES.items():

            if extracted[param] is not None:
                continue

            if any(re.search(rf"\b{alias}\b", line) for alias in aliases):

                numbers = re.findall(r"\d+\.\d+|\d+", line)

                if numbers:
                    # choose first decimal if exists (most lab values are decimals)
                    decimal_nums = [n for n in numbers if "." in n]

                    if decimal_nums:
                        value = decimal_nums[0]
                    else:
                        value = numbers[0]

                    extracted[param] = float(value)
    # ---------- PATIENT INFO ----------
    name = re.search(r"patient name\s*[:\-]\s*([a-z ]+?)(?:\n|age)", text, re.I)
    if name:
        extracted["patient_name"] = name.group(1).strip()

    age = re.search(r"age\s*[:\-]\s*(\d+)", text, re.I)
    if age:
        extracted["age"] = float(age.group(1))

    gender = re.search(r"\b(male|female)\b", text, re.I)
    if gender:
        extracted["gender"] = gender.group(1).lower()

    return extracted



# =========================================================
# CSV STORAGE
# =========================================================
def save_to_csv(patient_id: str, parameters: dict):

    os.makedirs("outputs", exist_ok=True)
    file_path = "outputs/parameters.csv"

    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=["patient_id"] + sorted(KNOWN_PARAMETERS)
        )

        if not file_exists:
            writer.writeheader()

        row = {"patient_id": patient_id}
        row.update(parameters)

        writer.writerow(row)


# =========================================================
# MASTER FUNCTION (CALL THIS FROM MAIN PIPELINE)
# =========================================================
def run_extraction(file_path: str, patient_id: str):

    text = extract_text(file_path)

    params = extract_parameters(text)

    save_to_csv(patient_id, params)

    return params
