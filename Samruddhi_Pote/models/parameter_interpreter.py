from utils.standard_ranges import STANDARD_RANGES


def _effective_range(param, context=None):
    if context is None:
        context = {}

    low, high = STANDARD_RANGES[param]

    gender = str(context.get("gender", "")).strip().lower()
    if param == "Hemoglobin":
        if gender == "male":
            return (13.0, 17.0)
        if gender == "female":
            return (12.0, 15.0)

    return (low, high)


def classify_value(param, value, context=None):
    low, high = _effective_range(param, context=context)

    if value < low:
        return "LOW"
    if value > high:
        return "HIGH"
    return "NORMAL"


def interpret_parameters(data, context=None):
    results = {}

    for param, value in data.items():
        if param in STANDARD_RANGES:
            results[param] = classify_value(param, value, context=context)

    return results


def interpret_severity(data, context=None):
    """Provide a coarse severity label for each interpreted parameter.

    Severity is intended for UI clarity (MILD / MODERATE / CRITICAL) and is
    not a medical diagnosis.
    """

    results = {}

    for param, value in data.items():
        if param not in STANDARD_RANGES:
            continue
        status = classify_value(param, value, context=context)
        results[param] = _severity_for(param, value, status, context=context)

    return results


def _severity_for(param, value, status, context=None):
    if status == "NORMAL":
        return "NORMAL"

    if param == "Platelets" and status == "LOW":
        if value < 50000:
            return "CRITICAL"
        if value < 150000:
            return "MODERATE"
        return "MILD"

    if param == "Hemoglobin" and status == "LOW":
        if value < 8.0:
            return "CRITICAL"
        if value < 10.0:
            return "MODERATE"
        return "MILD"

    if param == "WBC" and status == "HIGH":
        if value >= 20000:
            return "CRITICAL"
        if value >= 15000:
            return "MODERATE"
        return "MILD"

    if param == "Glucose" and status == "HIGH":
        if value >= 200:
            return "CRITICAL"
        if value >= 126:
            return "MODERATE"
        return "MILD"

    if param == "LDL" and status == "HIGH":
        if value >= 190:
            return "CRITICAL"
        if value >= 160:
            return "MODERATE"
        return "MILD"

    if param == "Triglycerides" and status == "HIGH":
        if value >= 500:
            return "CRITICAL"
        if value >= 200:
            return "MODERATE"
        return "MILD"

    if param == "Cholesterol" and status == "HIGH":
        if value >= 300:
            return "CRITICAL"
        if value >= 240:
            return "MODERATE"
        return "MILD"

    if param == "Creatinine" and status == "HIGH":
        if value >= 2.0:
            return "CRITICAL"
        return "MODERATE"

    if param == "HDL" and status == "LOW":
        if value < 30:
            return "MODERATE"
        return "MILD"

    # Default fallback for any other HIGH/LOW.
    return "MILD"
