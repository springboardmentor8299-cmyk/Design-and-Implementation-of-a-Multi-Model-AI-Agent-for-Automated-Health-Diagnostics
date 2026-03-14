import re
import hashlib
import random


_NAME_PATTERNS = [
    re.compile(
        r"^\s*(?:patient\s*)?name\s*[:\-]\s*(?P<name>.+?)\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r"^\s*patient\s*[:\-]\s*(?P<name>.+?)\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    ),
]

_AGE_PATTERN = re.compile(
    r"^\s*age\s*[:\-]\s*(?P<age>\d{1,3})\s*(?:years?|yrs?)?\b",
    flags=re.IGNORECASE | re.MULTILINE,
)

_GENDER_PATTERN = re.compile(
    r"^\s*(?:gender|sex)\s*[:\-]\s*(?P<gender>male|female|m|f)\b",
    flags=re.IGNORECASE | re.MULTILINE,
)


def extract_patient_metadata(raw_input):
    """Extract patient metadata (name, age, gender) from report text.

    Args:
        raw_input: Typically a text string from OCR/PDF parsing. If dict/list,
            attempts to read pre-populated metadata keys if present.

    Returns:
        Dict with optional keys: patient_name (str), age (int), gender (str, lowercased).
    """

    if isinstance(raw_input, str):
        return _extract_from_text(raw_input)

    # For JSON-like inputs, allow metadata passthrough if provided.
    if isinstance(raw_input, dict):
        meta = raw_input.get("metadata") if isinstance(raw_input.get("metadata"), dict) else {}
        out = {}
        name = meta.get("patient_name") or raw_input.get("patient_name") or meta.get("name") or raw_input.get("name")
        age = meta.get("age") or raw_input.get("age")
        gender = meta.get("gender") or raw_input.get("gender") or meta.get("sex") or raw_input.get("sex")

        if isinstance(name, str) and name.strip():
            out["patient_name"] = name.strip()
        if isinstance(age, (int, float)) and 0 < int(age) < 130:
            out["age"] = int(age)
        if isinstance(gender, str) and gender.strip():
            g = gender.strip().lower()
            out["gender"] = "male" if g in {"m", "male"} else "female" if g in {"f", "female"} else g
        return out

    return {}


def _extract_from_text(text):
    metadata = {}

    header = "\n".join(text.splitlines()[:60])

    for pattern in _NAME_PATTERNS:
        match = pattern.search(header)
        if match:
            name = _clean_name(match.group("name"))
            if name:
                metadata["patient_name"] = name
            break

    match = _AGE_PATTERN.search(header)
    if match:
        age = int(match.group("age"))
        if 0 < age < 130:
            metadata["age"] = age

    match = _GENDER_PATTERN.search(header)
    if match:
        g = match.group("gender").strip().lower()
        metadata["gender"] = "male" if g in {"m", "male"} else "female" if g in {"f", "female"} else g

    return metadata


def _clean_name(raw_name):
    if not raw_name:
        return ""

    name = raw_name.strip()
    # Remove common trailing delimiters or extra fields on the same line.
    for sep in ["|", "  ", "\t", ", age", ",age", " age", "gender", "sex"]:
        idx = name.lower().find(sep)
        if idx > 0 and sep in {"gender", "sex"}:
            name = name[:idx].strip(" -:|")
            break
        if idx > 0 and sep not in {"gender", "sex"}:
            name = name[:idx].strip(" -:|")
            break

    # Keep it reasonably bounded; OCR sometimes captures long junk lines.
    if len(name) > 80:
        name = name[:80].strip()

    # Basic sanity: must contain at least one letter.
    if not re.search(r"[A-Za-z]", name):
        return ""

    return name


DEFAULT_PATIENT_PROFILES = [
    {"patient_name": "Rahul Sharma", "age": 34, "gender": "male"},
    {"patient_name": "Ananya Iyer", "age": 29, "gender": "female"},
    {"patient_name": "Amit Patel", "age": 41, "gender": "male"},
    {"patient_name": "Priya Nair", "age": 36, "gender": "female"},
    {"patient_name": "Sanjay Gupta", "age": 52, "gender": "male"},
    {"patient_name": "Meera Singh", "age": 45, "gender": "female"},
]


def fill_missing_metadata(metadata, fallback_context=None, seed=None):
    """Fill missing patient fields so UI/output never shows empty values.

    Priority order per field:
      1) extracted metadata
      2) fallback_context (if provided)
      3) deterministic "random" default from DEFAULT_PATIENT_PROFILES
    """

    if metadata is None:
        metadata = {}
    if fallback_context is None:
        fallback_context = {}

    def _ctx(name):
        value = fallback_context.get(name)
        if isinstance(value, str):
            return value.strip()
        return value

    profile = _pick_default_profile(seed)

    out = dict(metadata)

    if not out.get("patient_name"):
        out["patient_name"] = _ctx("patient_name") or profile["patient_name"]

    if not out.get("age"):
        ctx_age = _ctx("age")
        out["age"] = int(ctx_age) if isinstance(ctx_age, (int, float)) and ctx_age else profile["age"]

    if not out.get("gender"):
        ctx_gender = _ctx("gender")
        if isinstance(ctx_gender, str) and ctx_gender:
            out["gender"] = ctx_gender.lower()
        else:
            out["gender"] = profile["gender"]

    return out


def _pick_default_profile(seed):
    if not DEFAULT_PATIENT_PROFILES:
        return {"patient_name": "Patient", "age": 35, "gender": "male"}

    if seed is None:
        # Keep stable in Streamlit reruns within a process.
        seed = "default-seed"

    if not isinstance(seed, (str, bytes)):
        seed = str(seed)

    if isinstance(seed, str):
        seed_bytes = seed.encode("utf-8", errors="ignore")
    else:
        seed_bytes = seed

    digest = hashlib.sha256(seed_bytes).digest()
    seed_int = int.from_bytes(digest[:8], "big", signed=False)

    rng = random.Random(seed_int)
    return rng.choice(DEFAULT_PATIENT_PROFILES)
