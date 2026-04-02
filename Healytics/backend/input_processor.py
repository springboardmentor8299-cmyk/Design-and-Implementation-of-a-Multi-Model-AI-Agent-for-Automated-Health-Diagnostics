# backend/input_processor.py
"""
Input Processing Module
Handles JSON reports, PDF blood reports, and manually entered values.
Validates and normalizes all inputs into a standard dictionary format.
"""

import json
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Keys we attempt to extract from free-text PDFs
PDF_PARAM_ALIASES = {
    "hemoglobin":        ["hemoglobin", "hgb", "hb"],
    "hematocrit":        ["hematocrit", "hct", "packed cell volume", "pcv"],
    "rbc":               ["rbc", "red blood cell", "red blood cells", "erythrocytes"],
    "wbc":               ["wbc", "white blood cell", "white blood cells", "leukocytes"],
    "platelets":         ["platelets", "plt", "thrombocytes"],
    "mcv":               ["mcv", "mean corpuscular volume"],
    "mch":               ["mch", "mean corpuscular hemoglobin"],
    "mchc":              ["mchc", "mean corpuscular hemoglobin concentration"],
    "total_cholesterol": ["total cholesterol", "cholesterol total", "cholesterol"],
    "ldl_cholesterol":   ["ldl", "ldl cholesterol", "low density lipoprotein"],
    "hdl_cholesterol":   ["hdl", "hdl cholesterol", "high density lipoprotein"],
    "triglycerides":     ["triglycerides", "tg", "triacylglycerol"],
    "vldl":              ["vldl"],
    "glucose_fasting":   ["fasting glucose", "fasting blood glucose", "fbg", "fbs"],
    "glucose":           ["glucose", "blood glucose", "rbs", "random blood sugar"],
    "hba1c":             ["hba1c", "glycated hemoglobin", "glycosylated hemoglobin", "a1c"],
    "insulin":           ["insulin", "fasting insulin"],
    "creatinine":        ["creatinine", "serum creatinine"],
    "bun":               ["bun", "blood urea nitrogen", "urea nitrogen", "urea"],
    "uric_acid":         ["uric acid", "serum uric acid"],
    "egfr":              ["egfr", "glomerular filtration", "gfr"],
    "alt":               ["alt", "alanine aminotransferase", "sgpt"],
    "ast":               ["ast", "aspartate aminotransferase", "sgot"],
    "alkaline_phosphatase": ["alkaline phosphatase", "alp", "alk phos"],
    "bilirubin_total":   ["total bilirubin", "bilirubin total", "bilirubin"],
    "bilirubin_direct":  ["direct bilirubin", "conjugated bilirubin"],
    "albumin":           ["albumin", "serum albumin"],
    "total_protein":     ["total protein", "serum total protein"],
    "tsh":               ["tsh", "thyroid stimulating hormone"],
    "t3":                ["t3", "triiodothyronine"],
    "t4":                ["t4", "thyroxine"],
    "free_t3":           ["free t3", "ft3"],
    "free_t4":           ["free t4", "ft4"],
    "sodium":            ["sodium", "na+", "na"],
    "potassium":         ["potassium", "k+", "k"],
    "calcium":           ["calcium", "ca++", "ca"],
    "chloride":          ["chloride", "cl-", "cl"],
    "bicarbonate":       ["bicarbonate", "co2", "hco3"],
    "magnesium":         ["magnesium", "mg"],
    "iron":              ["serum iron", "iron"],
    "ferritin":          ["ferritin", "serum ferritin"],
    "tibc":              ["tibc", "total iron binding capacity"],
    "crp":               ["crp", "c-reactive protein", "c reactive protein"],
    "hs_crp":            ["hs-crp", "high sensitivity crp", "hs crp"],
    "vitamin_d":         ["vitamin d", "25-oh vitamin d", "25 oh vitamin d", "25-hydroxyvitamin d"],
    "vitamin_b12":       ["vitamin b12", "b12", "cobalamin"],
    "folate":            ["folate", "folic acid"],
    "cortisol":          ["cortisol"],
    "testosterone":      ["testosterone", "total testosterone"],
}


class InputProcessor:
    """
    Validates, normalizes, and standardizes blood report data
    from multiple input formats into a uniform dictionary.
    """

    def process_json(self, json_data: dict) -> dict:
        """
        Accept a raw dict (from JSON upload or parsed JSON string).
        Normalize keys to lowercase_underscore format.
        Returns cleaned parameter dict + metadata.
        """
        result = {}
        metadata = {}
        numeric_fields = {}

        for raw_key, value in json_data.items():
            normalized_key = self._normalize_key(raw_key)

            # Separate metadata from numeric parameters
            if normalized_key in ("patient_name", "name"):
                metadata["patient_name"] = str(value)
            elif normalized_key == "age":
                try:
                    metadata["age"] = int(value)
                except (ValueError, TypeError):
                    pass
            elif normalized_key == "gender":
                metadata["gender"] = str(value).lower()
            elif normalized_key in ("medical_history", "history", "conditions"):
                metadata["medical_history"] = value
            else:
                # Try to parse as a numeric blood parameter
                numeric_val = self._extract_numeric(value)
                if numeric_val is not None:
                    numeric_fields[normalized_key] = numeric_val

        result["parameters"] = numeric_fields
        result["metadata"] = metadata
        return result

    def process_manual(self, manual_dict: dict) -> dict:
        """
        Process manually entered key-value pairs (already numeric).
        """
        parameters = {}
        for key, value in manual_dict.items():
            if value is not None and value != "":
                try:
                    parameters[key] = float(value)
                except (ValueError, TypeError):
                    pass

        return {
            "parameters": parameters,
            "metadata": {}
        }

    def process_pdf(self, pdf_path: str) -> dict:
        """
        Extract text from PDF and parse blood parameter values.
        Uses pdfplumber for text extraction + regex for value parsing.
        """
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber not installed. Run: pip install pdfplumber")
            return {"parameters": {}, "metadata": {}, "error": "pdfplumber not installed"}

        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            logger.error(f"PDF reading error: {e}")
            return {"parameters": {}, "metadata": {}, "error": str(e)}

        return self._parse_pdf_text(text)

    def process_pdf_bytes(self, pdf_bytes: bytes) -> dict:
        """
        Process PDF from uploaded bytes (Streamlit file uploader).
        """
        try:
            import pdfplumber
            import io
        except ImportError:
            return {"parameters": {}, "metadata": {}, "error": "pdfplumber not installed"}

        text = ""
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            return {"parameters": {}, "metadata": {}, "error": str(e)}

        return self._parse_pdf_text(text)

    # ── Private helpers ──────────────────────────────────────────────────────

    def _parse_pdf_text(self, text: str) -> dict:
        parameters = {}
        metadata = {}
        lines = text.lower().split("\n")

        # Try to extract patient metadata
        for line in lines:
            age_match = re.search(r"age[:\s]+(\d{1,3})", line)
            if age_match:
                metadata["age"] = int(age_match.group(1))
            gender_match = re.search(r"\b(male|female)\b", line)
            if gender_match:
                metadata["gender"] = gender_match.group(1)
            name_match = re.search(r"patient\s*name[:\s]+([a-z\s]+)", line)
            if name_match:
                metadata["patient_name"] = name_match.group(1).strip().title()

        # Try to extract parameter values
        for std_key, aliases in PDF_PARAM_ALIASES.items():
            for line in lines:
                for alias in aliases:
                    if alias in line:
                        # Look for a numeric value in the same line
                        nums = re.findall(r"(\d+\.?\d*)", line)
                        if nums:
                            try:
                                val = float(nums[0])
                                parameters[std_key] = val
                                break
                            except ValueError:
                                pass
                if std_key in parameters:
                    break

        return {"parameters": parameters, "metadata": metadata}

    def _normalize_key(self, key: str) -> str:
        """Convert CamelCase / spaced keys to snake_case."""
        key = str(key).strip()
        key = re.sub(r"([A-Z])", r"_\1", key).lower()
        key = re.sub(r"[\s\-]+", "_", key)
        key = re.sub(r"_+", "_", key).strip("_")
        return key

    def _extract_numeric(self, value) -> Optional[float]:
        """Attempt to parse a numeric value from various formats."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Strip units and extract first number
            match = re.search(r"(\d+\.?\d*)", value)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        return None

    def validate(self, processed: dict) -> dict:
        """
        Basic sanity checks on parameter values.
        Returns processed dict with a 'warnings' list added.
        """
        warnings = []
        params = processed.get("parameters", {})

        for key, value in params.items():
            if value < 0:
                warnings.append(f"Negative value for {key}: {value}. Ignoring.")
                params[key] = None
            if key == "hemoglobin" and value > 25:
                warnings.append(f"Hemoglobin {value} g/dL seems implausibly high.")
            if key in ("glucose", "glucose_fasting") and value > 700:
                warnings.append(f"Glucose {value} mg/dL seems implausibly high.")

        processed["warnings"] = warnings
        return processed