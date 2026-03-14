import re

from utils.standard_ranges import ALIASES, STANDARD_RANGES

PATTERNS = {}
for param in STANDARD_RANGES.keys():
    names = [param]

    for alias, canonical in ALIASES.items():
        if canonical == param:
            names.append(alias)

    name_pattern = "|".join(re.escape(n) for n in names)
    PATTERNS[param] = re.compile(
        rf"\b({name_pattern})\b\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:[a-zA-Z\/\^0-9]+)?",
        flags=re.IGNORECASE,
    )

TOTAL_CHOLESTEROL_PATTERN = re.compile(
    r"\bTotal\s+Cholesterol\b\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)",
    flags=re.IGNORECASE,
)

PARAM_HINTS = {
    "Hemoglobin": ["hemoglobin", "hgb", "hb"],
    "Glucose": [
        "glucose",
        "blood glucose",
        "fasting blood sugar",
        "fbs",
    ],
    "Cholesterol": [
        "cholesterol",
        "total cholesterol",
    ],
    "WBC": [
        "wbc",
        "white blood cell",
        "white blood cells",
        "total leukocyte count",
        "tlc",
    ],
    "Platelets": [
        "platelet",
        "platelets",
        "platelet count",
        "plt",
    ],
    "LDL": [
        "ldl",
        "ldl cholesterol",
    ],
    "HDL": [
        "hdl",
        "hdl cholesterol",
    ],
    "Triglycerides": [
        "triglycerides",
        "triglyceride",
        "tg",
    ],
    "Creatinine": [
        "creatinine",
        "serum creatinine",
    ],
}

NUMBER_PATTERN = re.compile(r"\b([0-9]+(?:\.[0-9]+)?)\b")


def _canonical_name(name):
    return ALIASES.get(name.strip(), name.strip())


def extract_parameters(raw_input):
    if isinstance(raw_input, (dict, list)):
        return _extract_from_json(raw_input)
    if isinstance(raw_input, str):
        return _extract_from_text(raw_input)
    raise ValueError("Unsupported input payload for extraction")


def _extract_from_text(text):
    extracted = {}

    for param, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            extracted[param] = float(match.group(2))

    if "Cholesterol" not in extracted:
        total_match = TOTAL_CHOLESTEROL_PATTERN.search(text)
        if total_match:
            extracted["Cholesterol"] = float(total_match.group(1))

    if len(extracted) < 3:
        _extract_from_tabular_text(text, extracted)

    unknown = _detect_unknown_parameters(text)
    if unknown:
        extracted["_unknown_parameters"] = unknown

    return extracted


def _detect_unknown_parameters(text):
    unknown = []

    # Common non-test header fields that often appear with ":" / "-"
    header_stopwords = {
        "name",
        "patient",
        "patient name",
        "age",
        "gender",
        "sex",
        "dob",
        "date",
        "sample",
        "collected",
        "reported",
        "ref",
        "reference",
        "laboratory",
        "lab",
        "doctor",
        "dr",
    }

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" not in line and "-" not in line:
            continue

        # Only consider lines that also contain a number (likely a result row).
        if not NUMBER_PATTERN.search(line):
            continue

        parts = re.split(r"[:\-]", line, maxsplit=1)
        if not parts:
            continue

        name = parts[0].strip()
        if not name:
            continue

        name_l = name.lower()
        if name_l in header_stopwords:
            continue

        # Skip canonical parameters and known aliases.
        if name in STANDARD_RANGES or name in ALIASES:
            continue

        # Avoid very long junk headings.
        if len(name) > 40:
            continue

        unknown.append(name)

    if not unknown:
        return []

    return sorted(set(unknown))


def _extract_from_json(payload):
    extracted = {}

    if isinstance(payload, list):
        iterable = payload
    elif isinstance(payload, dict):
        iterable = payload.items()
    else:
        return extracted

    if isinstance(payload, list):
        for item in iterable:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("parameter") or item.get("test")
            raw_value = item.get("value") or item.get("result")
            if not name or raw_value is None:
                continue
            canonical = _canonical_name(name)
            numeric = _to_float(raw_value)
            if numeric is not None:
                extracted[canonical] = numeric
    else:
        for key, value in iterable:
            canonical = _canonical_name(str(key))
            if isinstance(value, dict):
                raw_value = value.get("value", value.get("result"))
            else:
                raw_value = value
            numeric = _to_float(raw_value)
            if numeric is not None:
                extracted[canonical] = numeric

    return extracted


def _to_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        # Handles values like "110 mg/dL"
        match = re.search(r"[0-9]+(?:\.[0-9]+)?", value)
        if match:
            return float(match.group(0))
    return None


def _extract_from_tabular_text(text, extracted):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for param, hints in PARAM_HINTS.items():
        if param in extracted:
            continue

        for idx, line in enumerate(lines):
            line_l = line.lower()
            if not any(hint in line_l for hint in hints):
                continue

            for probe in range(idx, min(idx + 4, len(lines))):
                value = _to_float(lines[probe])
                if value is not None:
                    extracted[param] = value
                    break

            if param in extracted:
                break
