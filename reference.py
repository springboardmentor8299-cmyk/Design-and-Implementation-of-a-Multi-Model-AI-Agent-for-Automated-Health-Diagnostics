# Reference ranges (standard adult male, adjust later for age/gender)
REFERENCE_RANGES = {
    "Hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
    "WBC": {"min": 4500, "max": 11000, "unit": "/µL"},
    "Platelets": {"min": 150000, "max": 450000, "unit": "/µL"},
    "Glucose": {"min": 70, "max": 100, "unit": "mg/dL"},
    "Cholesterol": {"min": 125, "max": 200, "unit": "mg/dL"},
    "HDL": {"min": 40, "max": float('inf'), "unit": "mg/dL"},  # >40 is normal
}
def classify_value(value, param_name):
    """Return 'HIGH', 'LOW', or 'NORMAL' based on reference range."""
    if value is None:
        return "UNKNOWN"
    ranges = REFERENCE_RANGES.get(param_name)
    if not ranges:
        return "UNKNOWN"
    if value < ranges["min"]:
        return "LOW"
    if value > ranges.get("max", float('inf')):
        return "HIGH"
    return "NORMAL"