def detect_health_patterns(params):

    risks = {}

    glucose = params.get("fasting_plasma_glucose")
    hba1c = params.get("hba1c")

    chol = params.get("total_cholesterol")
    ldl = params.get("ldl_cholesterol")
    trig = params.get("triglycerides")
    hdl = params.get("hdl_cholesterol")

    creatinine = params.get("creatinine")
    urea = params.get("urea")

    tsh = params.get("tsh")
    hemoglobin = params.get("hemoglobin")
    age = params.get("age")
    gender = params.get("gender")

    # Diabetes risk
    # -------- Diabetes risk (FIXED) --------

    if glucose is not None:

        # Calculate score safely
        base_score = int((glucose / 200) * 50)
        if hba1c is not None:
            base_score += int((hba1c / 10) * 50)

        score = min(100, base_score)

        # 🔴 HIGH diabetes (both high)
        if glucose > 126 and (hba1c is not None and hba1c > 6.5):
            risks["Diabetes Risk"] = {
                "level": "HIGH",
                "score": score,
                "reason": "High glucose and HbA1c levels"
            }

        # 🟡 MEDIUM diabetes (even if HbA1c missing)
        elif glucose > 100 or (hba1c is not None and hba1c > 5.6):
            risks["Diabetes Risk"] = {
                "level": "MEDIUM",
                "score": min(70, score),
                "reason": "Elevated blood glucose level"
            }

    elif age and glucose:
        if age > 40 and glucose > 110:
            score = min(100, int((glucose / 200 + age / 100) * 50))

            risks["Diabetes Risk"] = {
                "level": "MEDIUM",
                "score": score,
                "reason": f"Age ({age}) and elevated glucose increase diabetes risk"
            }

    # Cardiovascular risk
    # Cardiovascular risk (FIXED)

    if chol and ldl and trig and hdl:

        risk_score = 0

        # Only add score if abnormal
        if chol > 200:
            risk_score += 30

        if ldl > 130:
            risk_score += 30

        if trig > 150:
            risk_score += 20

        if hdl < 40:
            risk_score += 20

        # Add age factor ONLY if already risky
        if risk_score > 0 and age and age > 45:
            risk_score += 10

        # Only add risk if abnormal
        if risk_score > 0:
            risks["Cardiovascular Risk"] = {
                "level": "HIGH" if risk_score > 50 else "MEDIUM",
                "score": min(100, risk_score),
                "reason": f"LDL: {ldl}, HDL: {hdl}, Triglycerides: {trig}"
            }

    # Thyroid disorder
    # -------- Thyroid risk (IMPROVED) --------

    if tsh is not None:

    # 🔴 HIGH (clearly abnormal)
        if tsh > 6:
            score = min(100, int((tsh / 10) * 100))

            risks["Thyroid Dysfunction Risk"] = {
                "level": "MEDIUM",
                "score": score,
                "reason": "Elevated TSH levels suggest possible thyroid dysfunction"
            }

        # 🟡 BORDERLINE (slightly high)
        elif tsh > 4:
            risks["Thyroid Dysfunction Risk"] = {
                "level": "LOW",
                "score": 30,
                "reason": "Slightly elevated TSH levels (borderline thyroid imbalance)"
            }

    # Kidney function issue
    if creatinine and urea:
        if creatinine > 1.3 and urea > 20:
            risks["Kidney Function Risk"] = "Possible kidney dysfunction"

    # Anemia
    # Anemia (context-aware)
    if hemoglobin:

        if gender == "female" and hemoglobin < 12:
            score = min(100, int((12 - hemoglobin) * 10))

            risks["Anemia Risk"] = {
                "level": "MEDIUM",
                "score": score,
                "reason": "Low hemoglobin (more critical in females)"
            }

        elif gender == "male" and hemoglobin < 13:
            score = min(100, int((13 - hemoglobin) * 10))

            risks["Anemia Risk"] = {
                "level": "MEDIUM",
                "score": score,
                "reason": "Low hemoglobin"
            }

    return risks