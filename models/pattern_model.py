def detect_risk(data, age, lifestyle=None):

    risks = []

    # 🔥 Helper function to assign level
    def get_level(score):
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Moderate"
        else:
            return "Low"

    # =========================
    # ❤️ CARDIOVASCULAR RISK
    # =========================
    cardio_score = 0

    if data.get("Cholesterol", 0) > 200:
        cardio_score += 30

    if data.get("LDL", 0) > 130:
        cardio_score += 25

    if data.get("HDL", 100) < 40:
        cardio_score += 20

    # Lifestyle impact 🔥
    if lifestyle:
        if lifestyle.get("smoking", "").lower() == "yes":
            cardio_score += 20

        if lifestyle.get("exercise", "").lower() in ["no", "low"]:
            cardio_score += 15

    if age and age > 45:
        cardio_score += 10

    if cardio_score > 0:
        risks.append({
            "name": "Cardiovascular",
            "score": cardio_score,
            "level": get_level(cardio_score),
            "reason": "Cholesterol levels and lifestyle factors indicate heart risk"
        })

    # =========================
    # 🩸 DIABETES RISK
    # =========================
    diabetes_score = 0

    if data.get("Glucose", 0) > 140:
        diabetes_score += 40
    elif data.get("Glucose", 0) > 110:
        diabetes_score += 20

    if lifestyle:
        if lifestyle.get("exercise", "").lower() in ["no", "low"]:
            diabetes_score += 10

        if lifestyle.get("sleep", "").lower() in ["poor", "low"]:
            diabetes_score += 10

    if age and age > 40:
        diabetes_score += 10

    if diabetes_score > 0:
        risks.append({
            "name": "Diabetes",
            "score": diabetes_score,
            "level": get_level(diabetes_score),
            "reason": "Elevated glucose levels detected"
        })

    # =========================
    # 🩸 ANEMIA RISK
    # =========================
    anemia_score = 0

    if data.get("Hemoglobin", 100) < 13:
        anemia_score += 40

    if anemia_score > 0:
        risks.append({
            "name": "Anemia",
            "score": anemia_score,
            "level": get_level(anemia_score),
            "reason": "Low hemoglobin detected"
        })

    # =========================
    # 🧪 INFECTION RISK
    # =========================
    if data.get("WBC", 0) > 11000:
        risks.append({
            "name": "Infection",
            "score": 50,
            "level": "Moderate",
            "reason": "High WBC count suggests infection"
        })

    # =========================
    # 🧬 CLOTTING RISK
    # =========================
    if data.get("Platelets", 0) > 450000:
        risks.append({
            "name": "Clot Risk",
            "score": 60,
            "level": "High",
            "reason": "High platelet count may increase clot risk"
        })

    return risks