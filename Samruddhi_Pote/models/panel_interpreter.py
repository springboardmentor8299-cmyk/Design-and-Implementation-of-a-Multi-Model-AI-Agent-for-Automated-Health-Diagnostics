import math


GLUCOSE_PREDIABETES_MIN = 100
GLUCOSE_DIABETES_MIN = 126
CHOLESTEROL_BORDERLINE_MIN = 200
CHOLESTEROL_HIGH_MIN = 240
LDL_BORDERLINE_MIN = 130
LDL_HIGH_MIN = 160
HDL_LOW_MAX = 40
TRIGLYCERIDES_HIGH_MIN = 150
WBC_HIGH_MIN = 11000
CREATININE_HIGH_MIN = 1.3
HEMOGLOBIN_LOW_MAX = 12
PLATELETS_LOW_MAX = 150000


def _assess_aip(value):
    if value < 0.1:
        return "LOW"
    if value <= 0.24:
        return "MEDIUM"
    return "HIGH"


def analyze_cbc(data):
    findings = []

    hemoglobin = data.get("Hemoglobin")
    if hemoglobin is not None and hemoglobin < HEMOGLOBIN_LOW_MAX:
        findings.append("Possible anemia (low hemoglobin)")

    wbc = data.get("WBC")
    if wbc is not None and wbc > WBC_HIGH_MIN:
        findings.append("Possible infection/inflammation (high WBC)")

    platelets = data.get("Platelets")
    if platelets is not None and platelets < PLATELETS_LOW_MAX:
        findings.append("Low platelet count")

    return findings


def analyze_lipid(data):
    findings = []

    cholesterol = data.get("Cholesterol")
    ldl = data.get("LDL")
    hdl = data.get("HDL")
    triglycerides = data.get("Triglycerides")

    if ldl is not None:
        if ldl > LDL_HIGH_MIN:
            findings.append("High cardiovascular risk (LDL very high)")
        elif ldl >= LDL_BORDERLINE_MIN:
            findings.append("LDL above optimal range")

    if cholesterol is not None:
        if cholesterol >= CHOLESTEROL_HIGH_MIN:
            findings.append("Total cholesterol high")
        elif cholesterol >= CHOLESTEROL_BORDERLINE_MIN:
            findings.append("Total cholesterol borderline high")

    if hdl is not None and hdl < HDL_LOW_MAX:
        findings.append("HDL low (reduced protective cholesterol)")

    if triglycerides is not None and triglycerides > TRIGLYCERIDES_HIGH_MIN:
        findings.append("Triglycerides elevated")

    if triglycerides is not None and hdl is not None and hdl > 0:
        tg_hdl_ratio = triglycerides / hdl
        aip = math.log10(tg_hdl_ratio)
        if _assess_aip(aip) == "HIGH":
            findings.append("High atherogenic index pattern")

    return findings


def analyze_blood_sugar(data):
    findings = []

    glucose = data.get("Glucose")
    if glucose is None:
        return findings

    if glucose >= GLUCOSE_DIABETES_MIN:
        findings.append("Glucose in diabetes range (confirm with repeat test)")
    elif GLUCOSE_PREDIABETES_MIN <= glucose < GLUCOSE_DIABETES_MIN:
        findings.append("Prediabetes risk pattern")

    return findings


def analyze_kidney(data):
    findings = []

    creatinine = data.get("Creatinine")
    if creatinine is not None and creatinine > CREATININE_HIGH_MIN:
        findings.append("Possible kidney function issue (creatinine elevated)")

    return findings


def analyze_panels(data, panels):
    """Generate simple panel-level interpretation based on detected panels.

    Args:
        data: Dict mapping canonical parameter name -> numeric value.
        panels: Output of models.panel_detector.detect_test_panels(data).

    Returns:
        Dict mapping panel name -> list of findings strings.
    """

    results = {}

    if "CBC" in panels:
        results["CBC"] = analyze_cbc(data)

    if "Lipid Profile" in panels:
        results["Lipid Profile"] = analyze_lipid(data)

    if "Blood Sugar" in panels:
        results["Blood Sugar"] = analyze_blood_sugar(data)

    if "Kidney Function" in panels:
        results["Kidney Function"] = analyze_kidney(data)

    # Cross-panel insights when multiple panels are present.
    glucose = data.get("Glucose")
    triglycerides = data.get("Triglycerides")
    hdl = data.get("HDL")
    if (
        glucose is not None
        and glucose >= GLUCOSE_PREDIABETES_MIN
        and triglycerides is not None
        and triglycerides > TRIGLYCERIDES_HIGH_MIN
        and hdl is not None
        and hdl < HDL_LOW_MAX
    ):
        target = "Blood Sugar" if "Blood Sugar" in results else "Lipid Profile"
        results.setdefault(target, []).append("Possible metabolic syndrome pattern")

    wbc = data.get("WBC")
    creatinine = data.get("Creatinine")
    if (
        wbc is not None
        and wbc > WBC_HIGH_MIN
        and creatinine is not None
        and creatinine > CREATININE_HIGH_MIN
    ):
        target = "Kidney Function" if "Kidney Function" in results else "CBC"
        results.setdefault(target, []).append(
            "Possible inflammatory or infection-related kidney stress"
        )

    return results

