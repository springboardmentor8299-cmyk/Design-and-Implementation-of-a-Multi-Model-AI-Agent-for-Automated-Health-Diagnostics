import re

# 🔥 Parameter mapping
PARAMETER_MAP = {
    "hemoglobin": "Hemoglobin",
    "hb": "Hemoglobin",
    "glucose": "Glucose",
    "blood sugar": "Glucose",
    "cholesterol": "Cholesterol",
    "total cholesterol": "Cholesterol",
    "ldl": "LDL",
    "hdl": "HDL",
    "triglycerides": "Triglycerides",
    "creatinine": "Creatinine",
    "urea": "Urea",
    "wbc": "WBC",
    "platelet": "Platelets"
}

# ✅ NORMALIZE NAME (FIXED)
def normalize_name(name):

    name = name.lower().strip()

    for key in PARAMETER_MAP:
        if key in name:
            return PARAMETER_MAP[key]

    return None


# ✅ RISK DETECTION (FIXED)
def detect_risks(data):

    risks = []

    if data.get("Glucose", 0) > 140:
        risks.append({
            "name": "Diabetes Risk",
            "reason": "High glucose level",
            "severity": "High"
        })

    if data.get("Cholesterol", 0) > 200:
        risks.append({
            "name": "Heart Disease Risk",
            "reason": "High cholesterol",
            "severity": "Medium"
        })

    if data.get("Hemoglobin", 100) < 13:
        risks.append({
            "name": "Anemia Risk",
            "reason": "Low hemoglobin",
            "severity": "Medium"
        })

    if data.get("WBC", 0) > 11000:
        risks.append({
            "name": "Infection Risk",
            "reason": "High WBC count",
            "severity": "Low"
        })

    return risks