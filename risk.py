import pandas as pd

# --------------------------------------------------
# Disease Risk Detection using Multiple Parameters
# --------------------------------------------------

def detect_health_risks(df):

    risks = []

    glucose = None
    hba1c = None
    cholesterol = None
    triglycerides = None
    hemoglobin = None
    wbc = None
    platelets = None

    # Extract values
    for _, row in df.iterrows():

        if row["Parameter"] == "Glucose":
            glucose = row["Value"]

        elif row["Parameter"] == "HbA1c":
            hba1c = row["Value"]

        elif row["Parameter"] == "Cholesterol":
            cholesterol = row["Value"]

        elif row["Parameter"] == "Triglycerides":
            triglycerides = row["Value"]

        elif row["Parameter"] == "Hemoglobin":
            hemoglobin = row["Value"]

        elif row["Parameter"] == "WBC":
            wbc = row["Value"]

        elif row["Parameter"] == "Platelets":
            platelets = row["Value"]

    # --------------------------------------------------
    # Diabetes Risk
    # --------------------------------------------------

    if glucose and glucose > 126:
        risks.append("High Glucose detected → Possible Diabetes")

    if hba1c and hba1c >= 6.5:
        risks.append("High HbA1c → Diabetes Risk")

    # --------------------------------------------------
    # Heart Disease Risk
    # --------------------------------------------------

    if cholesterol and cholesterol > 200:
        if triglycerides and triglycerides > 150:
            risks.append("High Cholesterol & Triglycerides → Heart Disease Risk")
        else:
            risks.append("High Cholesterol → Cardiovascular Risk")

    # --------------------------------------------------
    # Anemia Detection
    # --------------------------------------------------

    if hemoglobin and hemoglobin < 12:
        risks.append("Low Hemoglobin → Possible Anemia")

    # --------------------------------------------------
    # Infection Detection
    # --------------------------------------------------

    if wbc and wbc > 11000:
        risks.append("High WBC → Possible Infection")

    # --------------------------------------------------
    # Platelet Disorder
    # --------------------------------------------------

    if platelets and platelets < 150000:
        risks.append("Low Platelets → Platelet Disorder Risk")

    if not risks:
        risks.append("No major health risks detected")

    return risks


# --------------------------------------------------
# Health Recommendation Generator
# --------------------------------------------------

def generate_health_recommendations(risks):

    recommendations = []

    for risk in risks:

        if "Diabetes" in risk:
            recommendations.append(
                "Reduce sugar intake, exercise regularly, and consult a doctor."
            )

        elif "Heart" in risk or "Cardiovascular" in risk:
            recommendations.append(
                "Avoid oily food, maintain healthy weight, and monitor cholesterol."
            )

        elif "Anemia" in risk:
            recommendations.append(
                "Increase iron-rich foods such as spinach, beans, and red meat."
            )

        elif "Infection" in risk:
            recommendations.append(
                "Consult a physician and monitor WBC levels."
            )

        elif "Platelet" in risk:
            recommendations.append(
                "Seek medical advice and monitor platelet levels."
            )

        else:
            recommendations.append(
                "Maintain a balanced diet and regular health checkups."
            )

    return recommendations
