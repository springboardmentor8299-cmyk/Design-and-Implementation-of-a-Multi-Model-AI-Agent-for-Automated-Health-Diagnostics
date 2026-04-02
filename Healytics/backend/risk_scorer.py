# backend/risk_scorer.py
"""
Risk Scoring Module
Calculates:
  - Overall Health Score (0–100)
  - Cardiovascular Risk Score
  - TC/HDL Ratio
  - Diabetes Risk Score
  - Liver Risk Score
  - Kidney Risk Score
"""

import math


class RiskScorer:

    def calculate_all(self, parameters: dict, classified: list, metadata: dict = None) -> dict:
        meta   = metadata or {}
        gender = meta.get("gender", "general").lower()
        age    = int(meta.get("age", 40) or 40)

        scores = {
            "health_score":     self.health_score(classified),
            "cardiovascular":   self.cardiovascular_risk(parameters, gender, age),
            "diabetes":         self.diabetes_risk(parameters),
            "kidney":           self.kidney_risk(parameters, gender),
            "liver":            self.liver_risk(parameters, gender),
            "tc_hdl_ratio":     self.tc_hdl_ratio(parameters),
        }
        return scores

    # ── Health Score (0–100) ─────────────────────────────────────────────────

    def health_score(self, classified: list) -> dict:
        """
        Composite health score based on parameter classifications.
        Critical abnormality: -20 pts
        High/Low abnormality: -8 pts
        Score capped at 0–100, starting at 100.
        """
        if not classified:
            return {"score": 50, "label": "Insufficient Data", "color": "#9E9E9E"}

        score = 100
        for item in classified:
            severity = item.get("severity", "normal")
            if severity == "critical":
                score -= 20
            elif severity == "warning":
                score -= 8

        score = max(0, min(100, score))

        if score >= 85:
            label, color = "Excellent",    "#2ECC71"
        elif score >= 70:
            label, color = "Good",         "#27AE60"
        elif score >= 55:
            label, color = "Fair",         "#F39C12"
        elif score >= 40:
            label, color = "Below Average","#E67E22"
        else:
            label, color = "Poor",         "#E74C3C"

        return {"score": score, "label": label, "color": color}

    # ── Cardiovascular Risk ──────────────────────────────────────────────────

    def cardiovascular_risk(self, p: dict, gender: str, age: int) -> dict:
        """
        Simplified Framingham-inspired cardiovascular risk scoring.
        Returns risk percentage (10-year CVD risk estimate) and category.
        """
        risk_points = 0

        # Age factor
        if age < 35:
            risk_points += 0
        elif age < 45:
            risk_points += 4 if gender == "male" else 2
        elif age < 55:
            risk_points += 8 if gender == "male" else 5
        elif age < 65:
            risk_points += 11 if gender == "male" else 8
        else:
            risk_points += 14

        # Total Cholesterol
        tc = p.get("total_cholesterol")
        if tc:
            if tc < 160:   risk_points -= 3
            elif tc < 200: risk_points += 0
            elif tc < 240: risk_points += 4
            elif tc < 280: risk_points += 7
            else:          risk_points += 9

        # HDL
        hdl = p.get("hdl_cholesterol")
        if hdl:
            if hdl >= 60:   risk_points -= 1
            elif hdl >= 50: risk_points += 0
            elif hdl >= 40: risk_points += 1
            else:           risk_points += 2

        # LDL
        ldl = p.get("ldl_cholesterol")
        if ldl:
            if ldl >= 190:  risk_points += 5
            elif ldl >= 160: risk_points += 3
            elif ldl >= 130: risk_points += 1

        # Triglycerides
        tg = p.get("triglycerides")
        if tg:
            if tg >= 500:  risk_points += 5
            elif tg >= 200: risk_points += 2
            elif tg >= 150: risk_points += 1

        # Diabetes / glucose
        glc = p.get("glucose_fasting") or p.get("glucose")
        hba = p.get("hba1c")
        if (glc and glc >= 126) or (hba and hba >= 6.5):
            risk_points += 5
        elif (glc and glc >= 100) or (hba and hba >= 5.7):
            risk_points += 2

        # CRP
        crp = p.get("crp") or p.get("hs_crp")
        if crp and crp > 3:
            risk_points += 2

        # Gender adjustment
        if gender == "female":
            risk_points = max(0, risk_points - 3)

        # Convert points to percentage (rough mapping)
        risk_pct = min(95, max(1, risk_points * 2.5))
        risk_pct = round(risk_pct, 1)

        if risk_pct < 10:
            category, color = "Low",      "#2ECC71"
        elif risk_pct < 20:
            category, color = "Moderate", "#F39C12"
        elif risk_pct < 40:
            category, color = "High",     "#E67E22"
        else:
            category, color = "Very High","#E74C3C"

        return {
            "risk_pct":  risk_pct,
            "category":  category,
            "color":     color,
            "points":    risk_points,
        }

    # ── Diabetes Risk ────────────────────────────────────────────────────────

    def diabetes_risk(self, p: dict) -> dict:
        """Rule-based diabetes risk estimation."""
        risk = 0

        glc = p.get("glucose_fasting") or p.get("glucose")
        hba = p.get("hba1c")
        tg  = p.get("triglycerides")
        hdl = p.get("hdl_cholesterol")
        ins = p.get("insulin")

        if glc:
            if glc >= 126:   risk += 40
            elif glc >= 110: risk += 20
            elif glc >= 100: risk += 10
        if hba:
            if hba >= 6.5:   risk += 40
            elif hba >= 6.0: risk += 25
            elif hba >= 5.7: risk += 10
        if tg and tg >= 200: risk += 10
        if hdl and hdl < 40: risk += 10
        if ins and ins > 25: risk += 15

        risk = min(95, risk)

        if risk < 15:
            category, color = "Low",      "#2ECC71"
        elif risk < 35:
            category, color = "Moderate", "#F39C12"
        elif risk < 60:
            category, color = "High",     "#E67E22"
        else:
            category, color = "Very High","#E74C3C"

        return {"risk_pct": risk, "category": category, "color": color}

    # ── Kidney Risk ──────────────────────────────────────────────────────────

    def kidney_risk(self, p: dict, gender: str) -> dict:
        risk = 0
        cr   = p.get("creatinine")
        bun  = p.get("bun")
        egfr = p.get("egfr")
        ua   = p.get("uric_acid")

        cr_thresh = 1.04 if gender == "female" else 1.35
        if cr:
            if cr > cr_thresh * 2: risk += 40
            elif cr > cr_thresh:   risk += 20
        if bun and bun > 25:
            risk += 15 if bun > 40 else 8
        if egfr:
            if egfr < 30:   risk += 40
            elif egfr < 60: risk += 20
        if ua:
            ua_thresh = 6.0 if gender == "female" else 7.0
            if ua > ua_thresh: risk += 10

        risk = min(95, risk)
        if risk < 15:
            category, color = "Low",      "#2ECC71"
        elif risk < 40:
            category, color = "Moderate", "#F39C12"
        else:
            category, color = "High",     "#E74C3C"

        return {"risk_pct": risk, "category": category, "color": color}

    # ── Liver Risk ───────────────────────────────────────────────────────────

    def liver_risk(self, p: dict, gender: str) -> dict:
        risk = 0
        alt  = p.get("alt")
        ast  = p.get("ast")
        bili = p.get("bilirubin_total")
        alp  = p.get("alkaline_phosphatase")
        alb  = p.get("albumin")

        alt_thresh = 45 if gender == "female" else 56
        if alt:
            if alt > alt_thresh * 3: risk += 35
            elif alt > alt_thresh:   risk += 15
        if ast and ast > 40:
            risk += 15 if ast > 80 else 8
        if bili and bili > 1.2:
            risk += 20 if bili > 3 else 10
        if alp and alp > 147:
            risk += 10
        if alb and alb < 3.4:
            risk += 15

        risk = min(95, risk)
        if risk < 15:
            category, color = "Low",      "#2ECC71"
        elif risk < 40:
            category, color = "Moderate", "#F39C12"
        else:
            category, color = "High",     "#E74C3C"

        return {"risk_pct": risk, "category": category, "color": color}

    # ── TC/HDL Ratio ─────────────────────────────────────────────────────────

    def tc_hdl_ratio(self, p: dict) -> dict:
        tc  = p.get("total_cholesterol")
        hdl = p.get("hdl_cholesterol")

        if not tc or not hdl or hdl == 0:
            return {"ratio": None, "category": "N/A", "color": "#9E9E9E"}

        ratio = round(tc / hdl, 2)

        if ratio < 3.5:
            category, color = "Optimal",  "#2ECC71"
        elif ratio < 5.0:
            category, color = "Average",  "#F39C12"
        elif ratio < 6.0:
            category, color = "High Risk","#E67E22"
        else:
            category, color = "Very High","#E74C3C"

        return {"ratio": ratio, "category": category, "color": color}