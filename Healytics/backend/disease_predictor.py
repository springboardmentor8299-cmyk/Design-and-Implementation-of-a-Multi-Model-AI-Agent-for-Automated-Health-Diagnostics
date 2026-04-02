# backend/disease_predictor.py
"""
Disease Prediction Module
Estimates risk for common conditions using rule-based scoring.
Returns probability percentages and risk categories.
"""


class DiseasePredictor:

    def predict_all(self, parameters: dict, metadata: dict = None) -> list:
        meta   = metadata or {}
        gender = meta.get("gender", "general").lower()
        age    = int(meta.get("age", 40) or 40)

        predictions = [
            self._predict_type2_diabetes(parameters, gender, age),
            self._predict_heart_disease(parameters, gender, age),
            self._predict_anemia(parameters, gender),
            self._predict_hypothyroidism(parameters),
            self._predict_fatty_liver(parameters),
            self._predict_chronic_kidney_disease(parameters, gender),
        ]

        # Filter None results and sort by risk desc
        predictions = [p for p in predictions if p is not None]
        predictions.sort(key=lambda x: x["risk_pct"], reverse=True)
        return predictions

    # ── Individual Disease Predictions ────────────────────────────────────────

    def _predict_type2_diabetes(self, p, gender, age):
        score = 0
        glc = p.get("glucose_fasting") or p.get("glucose")
        hba = p.get("hba1c")
        tg  = p.get("triglycerides")
        hdl = p.get("hdl_cholesterol")
        ins = p.get("insulin")

        if glc:
            if glc >= 126: score += 40
            elif glc >= 110: score += 20
            elif glc >= 100: score += 10
        if hba:
            if hba >= 6.5: score += 40
            elif hba >= 6.0: score += 25
            elif hba >= 5.7: score += 12
        if tg and tg >= 150: score += 8
        if hdl and hdl < 40: score += 8
        if ins and ins > 25: score += 15
        if age > 45: score += 5
        if age > 60: score += 5

        risk = min(95, score)
        return self._format_prediction(
            name      = "Type 2 Diabetes",
            icon      = "🍬",
            risk_pct  = risk,
            key_params= ["glucose_fasting", "hba1c", "insulin"],
            description= "Risk estimate based on blood sugar markers, insulin resistance, and metabolic factors.",
        )

    def _predict_heart_disease(self, p, gender, age):
        score = 0
        tc  = p.get("total_cholesterol")
        ldl = p.get("ldl_cholesterol")
        hdl = p.get("hdl_cholesterol")
        tg  = p.get("triglycerides")
        crp = p.get("crp") or p.get("hs_crp")
        glc = p.get("glucose_fasting") or p.get("glucose")
        hba = p.get("hba1c")

        if tc and tc >= 240: score += 15
        elif tc and tc >= 200: score += 8
        if ldl and ldl >= 160: score += 15
        elif ldl and ldl >= 130: score += 8
        if hdl and hdl < 40: score += 12
        elif hdl and hdl < 50: score += 5
        if tg and tg >= 200: score += 10
        elif tg and tg >= 150: score += 5
        if crp and crp > 3: score += 12
        elif crp and crp > 1: score += 6
        if (glc and glc >= 126) or (hba and hba >= 6.5): score += 10
        elif (glc and glc >= 100) or (hba and hba >= 5.7): score += 5

        # Age & gender
        if gender == "male" and age > 45: score += 8
        elif gender == "female" and age > 55: score += 8
        elif age > 65: score += 10

        risk = min(95, score)
        return self._format_prediction(
            name      = "Coronary Heart Disease",
            icon      = "❤️",
            risk_pct  = risk,
            key_params= ["ldl_cholesterol", "hdl_cholesterol", "total_cholesterol", "crp"],
            description= "Risk estimate based on lipid panel, inflammation markers, and demographic factors.",
        )

    def _predict_anemia(self, p, gender):
        score = 0
        hgb  = p.get("hemoglobin")
        hct  = p.get("hematocrit")
        rbc  = p.get("rbc")
        mcv  = p.get("mcv")
        ferr = p.get("ferritin")

        low_hgb = 12.0 if gender == "female" else 13.5
        low_hct = 36.0 if gender == "female" else 41.0

        if hgb:
            if hgb < low_hgb - 3: score += 50
            elif hgb < low_hgb:   score += 30
        if hct and hct < low_hct: score += 20
        if rbc and rbc < 4.0:     score += 15
        if mcv and mcv < 80:      score += 10
        if ferr and ferr < 12:    score += 20

        risk = min(95, score)
        return self._format_prediction(
            name      = "Anemia",
            icon      = "🩸",
            risk_pct  = risk,
            key_params= ["hemoglobin", "hematocrit", "ferritin", "mcv"],
            description= "Risk estimate based on red blood cell parameters and iron stores.",
        )

    def _predict_hypothyroidism(self, p):
        tsh = p.get("tsh")
        t4  = p.get("t4") or p.get("free_t4")

        if not tsh:
            return None

        score = 0
        if tsh > 10: score += 70
        elif tsh > 4: score += 35
        if t4 and t4 < 5: score += 20

        risk = min(90, score)
        return self._format_prediction(
            name      = "Hypothyroidism",
            icon      = "🦋",
            risk_pct  = risk,
            key_params= ["tsh", "t4", "free_t4"],
            description= "Risk estimate based on thyroid hormone levels.",
        )

    def _predict_fatty_liver(self, p):
        alt  = p.get("alt")
        ast  = p.get("ast")
        tg   = p.get("triglycerides")
        glc  = p.get("glucose_fasting") or p.get("glucose")
        hba  = p.get("hba1c")

        score = 0
        if alt and alt > 56: score += 25
        elif alt and alt > 40: score += 12
        if ast and ast > 40: score += 15
        if tg and tg >= 150: score += 15
        if (glc and glc >= 100) or (hba and hba >= 5.7): score += 15

        risk = min(85, score)
        return self._format_prediction(
            name      = "Non-Alcoholic Fatty Liver (NAFLD)",
            icon      = "🫁",
            risk_pct  = risk,
            key_params= ["alt", "ast", "triglycerides"],
            description= "Risk estimate based on liver enzymes and metabolic markers.",
        )

    def _predict_chronic_kidney_disease(self, p, gender):
        cr   = p.get("creatinine")
        bun  = p.get("bun")
        egfr = p.get("egfr")
        ua   = p.get("uric_acid")

        cr_thresh = 1.04 if gender == "female" else 1.35
        score = 0
        if cr:
            if cr > cr_thresh * 2: score += 50
            elif cr > cr_thresh:   score += 25
        if bun and bun > 40: score += 25
        elif bun and bun > 25: score += 12
        if egfr:
            if egfr < 30:   score += 50
            elif egfr < 60: score += 30
        if ua:
            ua_thresh = 6 if gender == "female" else 7
            if ua > ua_thresh: score += 10

        risk = min(90, score)
        return self._format_prediction(
            name      = "Chronic Kidney Disease (CKD)",
            icon      = "🫘",
            risk_pct  = risk,
            key_params= ["creatinine", "egfr", "bun"],
            description= "Risk estimate based on kidney function markers.",
        )

    # ── Formatting helper ────────────────────────────────────────────────────

    def _format_prediction(self, name, icon, risk_pct, key_params, description):
        if risk_pct < 15:
            category, color = "Low Risk",       "#2ECC71"
        elif risk_pct < 35:
            category, color = "Moderate Risk",  "#F39C12"
        elif risk_pct < 60:
            category, color = "High Risk",      "#E67E22"
        else:
            category, color = "Very High Risk", "#E74C3C"

        return {
            "name":        name,
            "icon":        icon,
            "risk_pct":    risk_pct,
            "category":    category,
            "color":       color,
            "key_params":  key_params,
            "description": description,
        }