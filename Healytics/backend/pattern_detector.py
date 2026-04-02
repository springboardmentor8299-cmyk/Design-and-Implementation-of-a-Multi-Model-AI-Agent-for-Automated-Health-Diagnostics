# backend/pattern_detector.py
"""
Pattern Detection Engine (Model 2)
Analyzes combinations of parameters to identify clinically relevant patterns.
Uses rule-based logic grounded in established medical guidelines.
"""


class PatternDetector:

    def detect_all(self, parameters: dict, classified: list, metadata: dict = None) -> list:
        """
        Run all pattern checks and return a list of detected patterns.
        Each pattern is a dict with name, severity, description, related_params.
        """
        detected = []
        meta = metadata or {}
        gender = meta.get("gender", "general").lower()
        age    = meta.get("age", 40)

        checks = [
            self._check_metabolic_syndrome,
            self._check_cardiovascular_risk,
            self._check_anemia,
            self._check_iron_deficiency,
            self._check_diabetes_indicators,
            self._check_kidney_stress,
            self._check_liver_stress,
            self._check_thyroid_imbalance,
            self._check_infection_inflammation,
            self._check_vitamin_deficiency,
            self._check_electrolyte_imbalance,
            self._check_dyslipidemia,
        ]

        for check in checks:
            result = check(parameters, classified, gender, age)
            if result:
                detected.append(result)

        # Sort by severity
        order = {"high": 0, "moderate": 1, "low": 2, "info": 3}
        detected.sort(key=lambda x: order.get(x["severity"], 99))
        return detected

    # ── Pattern Checks ────────────────────────────────────────────────────────

    def _check_metabolic_syndrome(self, p, c, gender, age):
        """
        Metabolic syndrome: 3 of 5 criteria per ATP III / IDF guidelines.
        Criteria: high waist (not measurable), high TG, low HDL, high BP, high glucose.
        We assess 3 of 4 available markers.
        """
        criteria = []

        tg  = p.get("triglycerides")
        hdl = p.get("hdl_cholesterol")
        glc = p.get("glucose_fasting") or p.get("glucose")
        hba = p.get("hba1c")

        if tg and tg >= 150:
            criteria.append(f"Elevated triglycerides ({tg} mg/dL ≥ 150)")
        if hdl:
            hdl_thresh = 50 if gender == "female" else 40
            if hdl < hdl_thresh:
                criteria.append(f"Low HDL ({hdl} mg/dL < {hdl_thresh})")
        if glc and glc >= 100:
            criteria.append(f"Elevated fasting glucose ({glc} mg/dL ≥ 100)")
        if hba and hba >= 5.7:
            criteria.append(f"Elevated HbA1c ({hba}% ≥ 5.7)")

        if len(criteria) >= 2:
            return {
                "name":           "Metabolic Syndrome Indicators",
                "severity":       "high" if len(criteria) >= 3 else "moderate",
                "icon":           "⚠️",
                "description":    "Multiple metabolic risk factors detected, suggesting metabolic syndrome.",
                "criteria":       criteria,
                "related_params": ["triglycerides", "hdl_cholesterol", "glucose_fasting", "hba1c"],
                "advice":         "Consult a physician. Lifestyle changes (diet + exercise) are first-line treatment.",
            }
        return None

    def _check_cardiovascular_risk(self, p, c, gender, age):
        """High cardiovascular risk pattern."""
        risk_factors = []

        tc  = p.get("total_cholesterol")
        ldl = p.get("ldl_cholesterol")
        hdl = p.get("hdl_cholesterol")
        tg  = p.get("triglycerides")
        crp = p.get("crp") or p.get("hs_crp")

        if tc and tc >= 200:
            risk_factors.append(f"High total cholesterol ({tc} mg/dL)")
        if ldl and ldl >= 130:
            risk_factors.append(f"Elevated LDL ({ldl} mg/dL)")
        if hdl and hdl < 40:
            risk_factors.append(f"Low HDL ({hdl} mg/dL)")
        if tg and tg >= 200:
            risk_factors.append(f"Elevated triglycerides ({tg} mg/dL)")
        if crp and crp > 3.0:
            risk_factors.append(f"High CRP / inflammation marker ({crp} mg/L)")
        if age and age > 45 and gender == "male":
            risk_factors.append("Age > 45 (male) — inherent CV risk factor")
        if age and age > 55 and gender == "female":
            risk_factors.append("Age > 55 (female) — increased CV risk")

        if len(risk_factors) >= 2:
            return {
                "name":           "Elevated Cardiovascular Risk",
                "severity":       "high" if len(risk_factors) >= 3 else "moderate",
                "icon":           "❤️",
                "description":    "Pattern consistent with increased cardiovascular disease risk.",
                "criteria":       risk_factors,
                "related_params": ["total_cholesterol", "ldl_cholesterol", "hdl_cholesterol", "triglycerides"],
                "advice":         "Cardiac risk assessment by a physician is recommended. Consider lipid-lowering diet.",
            }
        return None

    def _check_anemia(self, p, c, gender, age):
        """Detect anemia pattern."""
        hgb = p.get("hemoglobin")
        hct = p.get("hematocrit")
        rbc = p.get("rbc")
        mcv = p.get("mcv")

        low_hgb_thresh = 12.0 if gender == "female" else 13.5
        low_hct_thresh = 36.0 if gender == "female" else 41.0

        if not hgb:
            return None

        if hgb < low_hgb_thresh:
            anemia_type = "unknown type"
            criteria = [f"Low hemoglobin ({hgb} g/dL)"]

            if mcv:
                if mcv < 80:
                    anemia_type = "Microcytic Anemia (possibly iron deficiency or thalassemia)"
                elif mcv > 100:
                    anemia_type = "Macrocytic Anemia (possibly B12 or folate deficiency)"
                else:
                    anemia_type = "Normocytic Anemia (check for chronic disease or blood loss)"
                criteria.append(f"MCV: {mcv} fL")

            if hct and hct < low_hct_thresh:
                criteria.append(f"Low hematocrit ({hct}%)")
            if rbc:
                criteria.append(f"RBC: {rbc} million/µL")

            return {
                "name":           f"Anemia — {anemia_type}",
                "severity":       "high" if hgb < 10 else "moderate",
                "icon":           "🩸",
                "description":    f"Hemoglobin below normal range. Pattern suggests {anemia_type}.",
                "criteria":       criteria,
                "related_params": ["hemoglobin", "hematocrit", "rbc", "mcv"],
                "advice":         "Further evaluation recommended. Treatment depends on underlying cause.",
            }
        return None

    def _check_iron_deficiency(self, p, c, gender, age):
        """Iron deficiency pattern."""
        iron     = p.get("iron")
        ferritin = p.get("ferritin")
        tibc     = p.get("tibc")
        mcv      = p.get("mcv")

        criteria = []
        if iron and iron < 60:
            criteria.append(f"Low serum iron ({iron} µg/dL)")
        if ferritin:
            thresh = 12 if gender == "female" else 24
            if ferritin < thresh:
                criteria.append(f"Low ferritin ({ferritin} ng/mL)")
        if tibc and tibc > 370:
            criteria.append(f"Elevated TIBC ({tibc} µg/dL) — indicating iron deficiency")
        if mcv and mcv < 80:
            criteria.append(f"Low MCV ({mcv} fL) — microcytic")

        if len(criteria) >= 2:
            return {
                "name":           "Iron Deficiency Pattern",
                "severity":       "moderate",
                "icon":           "🔩",
                "description":    "Multiple iron-related markers suggest iron deficiency.",
                "criteria":       criteria,
                "related_params": ["iron", "ferritin", "tibc", "mcv"],
                "advice":         "Iron supplementation and dietary iron increase may be needed. Confirm with physician.",
            }
        return None

    def _check_diabetes_indicators(self, p, c, gender, age):
        """Pre-diabetes or diabetes indicator pattern."""
        glc = p.get("glucose_fasting") or p.get("glucose")
        hba = p.get("hba1c")
        ins = p.get("insulin")

        criteria = []
        if glc and glc >= 126:
            criteria.append(f"Fasting glucose ≥ 126 mg/dL ({glc}) — Diabetic range")
        elif glc and glc >= 100:
            criteria.append(f"Fasting glucose 100–125 mg/dL ({glc}) — Pre-diabetic range")
        if hba and hba >= 6.5:
            criteria.append(f"HbA1c ≥ 6.5% ({hba}%) — Diabetic range")
        elif hba and hba >= 5.7:
            criteria.append(f"HbA1c 5.7–6.4% ({hba}%) — Pre-diabetic range")
        if ins and ins > 25:
            criteria.append(f"Elevated fasting insulin ({ins} µIU/mL) — possible insulin resistance")

        if criteria:
            is_diabetic = any("Diabetic range" in c for c in criteria)
            return {
                "name":           "Diabetes / Pre-diabetes Indicators",
                "severity":       "high" if is_diabetic else "moderate",
                "icon":           "🍬",
                "description":    "Blood sugar markers suggest diabetes or pre-diabetes.",
                "criteria":       criteria,
                "related_params": ["glucose_fasting", "hba1c", "insulin"],
                "advice":         "Lifestyle modification (diet, exercise) critical. Medical evaluation recommended.",
            }
        return None

    def _check_kidney_stress(self, p, c, gender, age):
        """Kidney stress / dysfunction pattern."""
        cr  = p.get("creatinine")
        bun = p.get("bun")
        ua  = p.get("uric_acid")
        egfr = p.get("egfr")

        cr_thresh = 1.04 if gender == "female" else 1.35

        criteria = []
        if cr and cr > cr_thresh:
            criteria.append(f"Elevated creatinine ({cr} mg/dL)")
        if bun and bun > 25:
            criteria.append(f"Elevated BUN ({bun} mg/dL)")
        if ua:
            ua_thresh = 6.0 if gender == "female" else 7.0
            if ua > ua_thresh:
                criteria.append(f"Elevated uric acid ({ua} mg/dL)")
        if egfr and egfr < 60:
            criteria.append(f"Reduced eGFR ({egfr} mL/min/1.73m²) — possible CKD")

        if len(criteria) >= 2:
            return {
                "name":           "Kidney Stress Indicators",
                "severity":       "high" if (egfr and egfr < 60) else "moderate",
                "icon":           "🫘",
                "description":    "Multiple kidney function markers are abnormal.",
                "criteria":       criteria,
                "related_params": ["creatinine", "bun", "uric_acid", "egfr"],
                "advice":         "Adequate hydration and nephrology follow-up recommended.",
            }
        return None

    def _check_liver_stress(self, p, c, gender, age):
        """Liver dysfunction pattern."""
        alt  = p.get("alt")
        ast  = p.get("ast")
        bili = p.get("bilirubin_total")
        alp  = p.get("alkaline_phosphatase")
        alb  = p.get("albumin")

        alt_thresh = 45 if gender == "female" else 56
        criteria = []
        if alt and alt > alt_thresh:
            criteria.append(f"Elevated ALT ({alt} U/L)")
        if ast and ast > 40:
            criteria.append(f"Elevated AST ({ast} U/L)")
        if bili and bili > 1.2:
            criteria.append(f"Elevated bilirubin ({bili} mg/dL)")
        if alp and alp > 147:
            criteria.append(f"Elevated ALP ({alp} U/L)")
        if alb and alb < 3.4:
            criteria.append(f"Low albumin ({alb} g/dL)")

        if len(criteria) >= 2:
            return {
                "name":           "Liver Function Abnormality",
                "severity":       "high" if len(criteria) >= 3 else "moderate",
                "icon":           "🫁",
                "description":    "Multiple liver function markers are outside normal range.",
                "criteria":       criteria,
                "related_params": ["alt", "ast", "bilirubin_total", "alkaline_phosphatase"],
                "advice":         "Avoid hepatotoxic substances (alcohol, certain medications). Hepatology consult advised.",
            }
        return None

    def _check_thyroid_imbalance(self, p, c, gender, age):
        tsh = p.get("tsh")
        t3  = p.get("t3") or p.get("free_t3")
        t4  = p.get("t4") or p.get("free_t4")

        if not tsh:
            return None

        if tsh > 4.0:
            return {
                "name":           "Possible Hypothyroidism",
                "severity":       "moderate",
                "icon":           "🦋",
                "description":    f"Elevated TSH ({tsh} mIU/L) suggests underactive thyroid.",
                "criteria":       [f"TSH: {tsh} mIU/L (> 4.0)"],
                "related_params": ["tsh", "t3", "t4"],
                "advice":         "Thyroid panel confirmation and endocrinology consultation recommended.",
            }
        elif tsh < 0.4:
            return {
                "name":           "Possible Hyperthyroidism",
                "severity":       "moderate",
                "icon":           "🦋",
                "description":    f"Suppressed TSH ({tsh} mIU/L) suggests overactive thyroid.",
                "criteria":       [f"TSH: {tsh} mIU/L (< 0.4)"],
                "related_params": ["tsh", "t3", "t4"],
                "advice":         "Follow-up thyroid function tests and endocrinology consult recommended.",
            }
        return None

    def _check_infection_inflammation(self, p, c, gender, age):
        wbc = p.get("wbc")
        crp = p.get("crp") or p.get("hs_crp")

        criteria = []
        if wbc and wbc > 11.0:
            criteria.append(f"Elevated WBC ({wbc} thousand/µL) — possible infection or inflammation")
        elif wbc and wbc < 4.5:
            criteria.append(f"Low WBC ({wbc} thousand/µL) — possible immune suppression")
        if crp and crp > 10:
            criteria.append(f"Elevated CRP ({crp} mg/L) — active inflammation")
        elif crp and crp > 3:
            criteria.append(f"Moderately elevated CRP ({crp} mg/L)")

        if criteria:
            return {
                "name":           "Infection / Inflammation Markers",
                "severity":       "high" if (wbc and wbc > 15) else "moderate",
                "icon":           "🦠",
                "description":    "Elevated immune markers suggest possible infection or systemic inflammation.",
                "criteria":       criteria,
                "related_params": ["wbc", "crp", "hs_crp"],
                "advice":         "Clinical evaluation recommended to identify source of infection or inflammation.",
            }
        return None

    def _check_vitamin_deficiency(self, p, c, gender, age):
        vd   = p.get("vitamin_d")
        b12  = p.get("vitamin_b12")
        fol  = p.get("folate")

        criteria = []
        if vd and vd < 20:
            criteria.append(f"Vitamin D deficient ({vd} ng/mL < 20)")
        elif vd and vd < 30:
            criteria.append(f"Vitamin D insufficient ({vd} ng/mL, 20–30)")
        if b12 and b12 < 200:
            criteria.append(f"Low Vitamin B12 ({b12} pg/mL)")
        if fol and fol < 2.7:
            criteria.append(f"Low folate ({fol} ng/mL)")

        if criteria:
            return {
                "name":           "Vitamin / Micronutrient Deficiency",
                "severity":       "moderate",
                "icon":           "💊",
                "description":    "Suboptimal vitamin levels detected.",
                "criteria":       criteria,
                "related_params": ["vitamin_d", "vitamin_b12", "folate"],
                "advice":         "Supplementation and dietary adjustment recommended. Discuss with physician.",
            }
        return None

    def _check_electrolyte_imbalance(self, p, c, gender, age):
        na = p.get("sodium")
        k  = p.get("potassium")
        ca = p.get("calcium")

        criteria = []
        if na and (na < 136 or na > 145):
            criteria.append(f"Abnormal sodium ({na} mEq/L)")
        if k and (k < 3.5 or k > 5.0):
            criteria.append(f"Abnormal potassium ({k} mEq/L)")
        if ca and (ca < 8.5 or ca > 10.5):
            criteria.append(f"Abnormal calcium ({ca} mg/dL)")

        if len(criteria) >= 2:
            return {
                "name":           "Electrolyte Imbalance",
                "severity":       "moderate",
                "icon":           "⚡",
                "description":    "Multiple electrolytes are outside normal range.",
                "criteria":       criteria,
                "related_params": ["sodium", "potassium", "calcium"],
                "advice":         "Electrolyte correction and hydration status evaluation recommended.",
            }
        return None

    def _check_dyslipidemia(self, p, c, gender, age):
        tc  = p.get("total_cholesterol")
        ldl = p.get("ldl_cholesterol")
        hdl = p.get("hdl_cholesterol")
        tg  = p.get("triglycerides")

        if not any([tc, ldl, hdl, tg]):
            return None

        criteria = []
        tc_hdl_ratio = None
        if tc and hdl and hdl > 0:
            tc_hdl_ratio = round(tc / hdl, 2)
            if tc_hdl_ratio > 5.0:
                criteria.append(f"High TC/HDL ratio ({tc_hdl_ratio} > 5.0) — cardiovascular risk indicator")

        if ldl and ldl >= 160:
            criteria.append(f"High LDL cholesterol ({ldl} mg/dL ≥ 160)")
        if tg and tg >= 500:
            criteria.append(f"Very high triglycerides ({tg} mg/dL ≥ 500) — pancreatitis risk")
        elif tg and tg >= 200:
            criteria.append(f"High triglycerides ({tg} mg/dL)")

        if criteria:
            return {
                "name":           "Dyslipidemia",
                "severity":       "moderate",
                "icon":           "📊",
                "description":    "Abnormal blood lipid profile consistent with dyslipidemia.",
                "criteria":       criteria,
                "tc_hdl_ratio":   tc_hdl_ratio,
                "related_params": ["total_cholesterol", "ldl_cholesterol", "hdl_cholesterol", "triglycerides"],
                "advice":         "Low-fat diet, exercise, and possible statin therapy consultation recommended.",
            }
        return None