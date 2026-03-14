import json
import os
import shutil

import cv2
import pdfplumber
import pytesseract

TESSERACT_COMMON_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def parse_input(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(file_path)
    if ext in [".png", ".jpg", ".jpeg"]:
        return parse_image(file_path)
    if ext == ".json":
        return parse_json(file_path)

    raise ValueError("Unsupported file format. Use PDF, image, or JSON.")


def parse_pdf(file_path):
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_image(file_path):
    _configure_tesseract()

    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Unable to read image file: {file_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    try:
        # Multiple OCR passes improve robustness across different report templates.
        candidates = []

        candidates.append(
            pytesseract.image_to_string(gray, config="--oem 1 --psm 6")
        )

        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2,
        )
        candidates.append(
            pytesseract.image_to_string(thresh, config="--oem 1 --psm 6")
        )

        _, otsu = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        candidates.append(
            pytesseract.image_to_string(otsu, config="--oem 1 --psm 6")
        )

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel, iterations=1)
        candidates.append(
            pytesseract.image_to_string(cleaned, config="--oem 1 --psm 4")
        )

        scaled = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        candidates.append(
            pytesseract.image_to_string(scaled, config="--oem 1 --psm 11")
        )

        best_text = max(candidates, key=_score_ocr_text)
        return best_text
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR not found. Install tesseract and set TESSERACT_CMD if needed."
        ) from exc


def parse_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _configure_tesseract():
    env_path = os.getenv("TESSERACT_CMD")
    if env_path:
        pytesseract.pytesseract.tesseract_cmd = env_path
        return

    tesseract_bin = shutil.which("tesseract")
    if tesseract_bin:
        pytesseract.pytesseract.tesseract_cmd = tesseract_bin
        return

    for path in TESSERACT_COMMON_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return


def _score_ocr_text(text):
    if not text:
        return 0

    text_l = text.lower()
    keywords = [
        "hemoglobin",
        "glucose",
        "cholesterol",
        "hdl",
        "ldl",
        "triglycerides",
        "platelet",
        "wbc",
        "creatinine",
    ]
    hit_count = sum(1 for keyword in keywords if keyword in text_l)
    return hit_count * 100 + len(text)
