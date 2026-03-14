import math

from models.panel_detector import detect_test_panels
from models.panel_interpreter import analyze_panels

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
PLATELETS_LOW_MIN = 150000
PLATELETS_CRITICAL_MIN = 50000


def _assess_aip(value):
    if value < 0.1:
        return "LOW"
    if value <= 0.24:
        return "MEDIUM"
    return "HIGH"


def calculate_derived_metrics(data):
    metrics = {}

    cholesterol = data.get("Cholesterol", data.get("Total Cholesterol"))
    hdl = data.get("HDL")
    ldl = data.get("LDL")
    triglycerides = data.get("Triglycerides")

    if cholesterol and hdl and hdl > 0:
        ratio = cholesterol / hdl
        metrics["cholesterol_hdl_ratio"] = round(ratio, 2)
        metrics["cholesterol_hdl_assessment"] = (
            "HIGH" if ratio > 5.0 else "BORDERLINE" if ratio > 3.5 else "NORMAL"
        )
        non_hdl = cholesterol - hdl
        metrics["non_hdl_cholesterol"] = round(non_hdl, 2)
        if non_hdl > 190:
            metrics["non_hdl_assessment"] = "HIGH"
        elif non_hdl > 160:
            metrics["non_hdl_assessment"] = "BORDERLINE"
        else:
            metrics["non_hdl_assessment"] = "NORMAL"

    if ldl and hdl and hdl > 0:
        ratio = ldl / hdl
        metrics["ldl_hdl_ratio"] = round(ratio, 2)
        metrics["ldl_hdl_assessment"] = (
            "HIGH" if ratio > 3.5 else "BORDERLINE" if ratio > 2.5 else "NORMAL"
        )

    if triglycerides and hdl and hdl > 0:
        tg_hdl_ratio = triglycerides / hdl
        metrics["tg_hdl_ratio"] = round(tg_hdl_ratio, 2)
        aip = math.log10(tg_hdl_ratio)
        metrics["atherogenic_index"] = round(aip, 2)
        metrics["atherogenic_index_assessment"] = _assess_aip(aip)

    return metrics


def calculate_confidence(data):
    required = [
        "Glucose",
        "Cholesterol",
        "HDL",
        "LDL",
        "Triglycerides",
        "Hemoglobin",
        "WBC",
        "Platelets",
        "Creatinine",
    ]
    present = sum(1 for p in required if p in data)
    return round((present / len(required)) * 100, 1)


def detect_patterns(data, panels=None):
    patterns = []

    if panels is None:
        panels = detect_test_panels(data)

    panel_results = analyze_panels(data, panels)
    for panel, findings in panel_results.items():
        for finding in findings:
            patterns.append(f"{panel}: {finding}")

    if data.get("Glucose", 0) >= GLUCOSE_DIABETES_MIN:
        patterns.append("Possible diabetes pattern detected")

    if data.get("Triglycerides", 0) > TRIGLYCERIDES_HIGH_MIN and data.get("HDL", 100) < HDL_LOW_MAX:
        patterns.append("Metabolic syndrome risk pattern")

    return patterns


def calculate_health_risk(data, panels=None):
    score = 0
    reasons = []

    def add(points, reason):
        nonlocal score
        score += points
        reasons.append(reason)

    if panels is None:
        panels = detect_test_panels(data)
    panel_names = set(panels.keys())

    glucose = data.get("Glucose")
    cholesterol = data.get("Cholesterol", data.get("Total Cholesterol"))
    triglycerides = data.get("Triglycerides")
    ldl = data.get("LDL")
    hdl = data.get("HDL")
    hemoglobin = data.get("Hemoglobin")
    creatinine = data.get("Creatinine")
    wbc = data.get("WBC")
    platelets = data.get("Platelets")

    if glucose is not None:
        if glucose >= GLUCOSE_DIABETES_MIN:
            add(
                3,
                "Blood Sugar: glucose in diabetes range"
                if "Blood Sugar" in panel_names
                else "Glucose in diabetes range",
            )
        elif GLUCOSE_PREDIABETES_MIN <= glucose < GLUCOSE_DIABETES_MIN:
            add(
                2,
                "Blood Sugar: glucose in prediabetes range"
                if "Blood Sugar" in panel_names
                else "Glucose in prediabetes range",
            )

    # Lipids: cap total contribution to avoid double counting correlated risks.
    lipid_items = []
    if ldl is not None:
        if ldl > LDL_HIGH_MIN:
            lipid_items.append((3, "LDL very high"))
        elif ldl >= LDL_BORDERLINE_MIN:
            lipid_items.append((2, "LDL elevated"))

    if hdl is not None and hdl < HDL_LOW_MAX:
        lipid_items.append((2, "HDL low"))

    if triglycerides is not None and triglycerides > TRIGLYCERIDES_HIGH_MIN:
        lipid_items.append((2, "Triglycerides elevated"))

    if cholesterol is not None:
        if cholesterol >= CHOLESTEROL_HIGH_MIN:
            lipid_items.append((3, "Total cholesterol high"))
        elif cholesterol >= CHOLESTEROL_BORDERLINE_MIN:
            lipid_items.append((2, "Total cholesterol borderline high"))

    if lipid_items:
        lipid_points = sum(item[0] for item in lipid_items)
        lipid_cap = 4
        add(
            min(lipid_points, lipid_cap),
            "Lipid Profile: atherogenic lipid profile burden"
            if "Lipid Profile" in panel_names
            else "Atherogenic lipid profile burden",
        )
        for _, reason in lipid_items[:3]:
            reasons.append(
                f"Lipid Profile: {reason}" if "Lipid Profile" in panel_names else reason
            )

    if creatinine is not None and wbc is not None and creatinine > CREATININE_HIGH_MIN and wbc > WBC_HIGH_MIN:
        add(
            3,
            "Kidney Function: creatinine and WBC suggest inflammatory kidney stress"
            if "Kidney Function" in panel_names or "CBC" in panel_names
            else "Creatinine and WBC suggest inflammatory kidney stress",
        )
    else:
        if creatinine is not None and creatinine > CREATININE_HIGH_MIN:
            add(
                1,
                "Kidney Function: creatinine above normal range"
                if "Kidney Function" in panel_names
                else "Creatinine above normal range",
            )
        if wbc is not None and wbc > WBC_HIGH_MIN:
            add(
                2,
                "CBC: WBC above normal range" if "CBC" in panel_names else "WBC above normal range",
            )

    if hemoglobin is not None and hemoglobin < HEMOGLOBIN_LOW_MAX:
        add(
            1,
            "CBC: hemoglobin below normal" if "CBC" in panel_names else "Hemoglobin below normal",
        )

    if platelets is not None:
        if platelets < PLATELETS_CRITICAL_MIN:
            add(
                4,
                "CBC: critically low platelet count"
                if "CBC" in panel_names
                else "Critically low platelet count",
            )
        elif platelets < PLATELETS_LOW_MIN:
            add(
                2,
                "CBC: platelet count below normal"
                if "CBC" in panel_names
                else "Platelet count below normal",
            )

    derived = calculate_derived_metrics(data)
    if derived.get("atherogenic_index_assessment") == "HIGH":
        add(
            2,
            "Lipid Profile: atherogenic index high"
            if "Lipid Profile" in panel_names
            else "Atherogenic index high",
        )
    elif derived.get("atherogenic_index_assessment") == "MEDIUM":
        add(
            1,
            "Lipid Profile: atherogenic index borderline"
            if "Lipid Profile" in panel_names
            else "Atherogenic index borderline",
        )

    if score >= 8:
        level = "HIGH"
    elif score >= 4:
        level = "MEDIUM"
    else:
        level = "LOW"

    confidence = calculate_confidence(data)
    health_score = max(0, 100 - score * 12)

    summary = "Overall profile appears clinically stable."
    if level == "MEDIUM":
        summary = "Some abnormal indicators detected that may require lifestyle changes."
    if level == "HIGH":
        summary = "Multiple abnormal indicators detected. Medical consultation recommended."

    return {
        "risk_score": score,
        "risk_level": level,
        "summary": summary,
        "risk_factors": reasons,
        "derived_metrics": derived,
        "confidence_score": confidence,
        "health_score": health_score,
    }


def generate_recommendations(data, interpretation):
    recommendations = []

    if interpretation.get("Glucose") == "HIGH":
        recommendations.append(
            "Limit refined carbohydrates (sugary drinks, sweets) and increase fiber intake from vegetables and whole grains."
        )
        recommendations.append(
            "Repeat fasting glucose or HbA1c in 3 months and discuss diabetes screening with a clinician."
        )
    if interpretation.get("LDL") == "HIGH" or interpretation.get("Cholesterol") == "HIGH":
        recommendations.append(
            "Reduce saturated/trans fats, prefer unsaturated fats, and increase soluble fiber (oats, legumes, fruits)."
        )
        recommendations.append(
            "Repeat lipid profile in 3-6 months after lifestyle modifications."
        )
    if interpretation.get("HDL") == "LOW":
        recommendations.append(
            "Increase aerobic activity, avoid smoking, and include healthy fat sources such as nuts, seeds, and olive oil."
        )
    if interpretation.get("Triglycerides") == "HIGH":
        recommendations.append(
            "Limit alcohol and refined sugars, improve carbohydrate quality, and target gradual weight reduction."
        )
    if interpretation.get("Hemoglobin") == "LOW":
        recommendations.append(
            "Review dietary iron, B12, and folate intake; consider repeat CBC and clinical anemia workup if symptomatic."
        )
    if interpretation.get("Platelets") == "LOW":
        recommendations.append(
            "Low platelet count detected. Avoid activities that increase bleeding risk and consult a physician."
        )
    if data.get("Platelets", 999999) < PLATELETS_CRITICAL_MIN:
        recommendations.append(
            "Critically low platelet count detected. Immediate medical evaluation is recommended."
        )
    if interpretation.get("Creatinine") == "HIGH":
        recommendations.append(
            "Maintain hydration, avoid unnecessary nephrotoxic medications, and schedule kidney function follow-up."
        )

    if not recommendations:
        recommendations.append(
            "No major abnormalities detected; continue preventive care, balanced nutrition, and routine periodic health checkups."
        )

    return recommendations
