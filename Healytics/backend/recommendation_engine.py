# backend/recommendation_engine.py
"""
Personalized Recommendation Generator (Model 3)
Produces actionable diet, lifestyle, and medical advice
linked to specific findings from the analysis.
"""


class RecommendationEngine:

    def generate(self, classified: list, patterns: list, scores: dict, metadata: dict = None) -> dict:
        """
        Returns recommendations grouped by category:
          - cardiovascular
          - nutrition / diet
          - lifestyle
          - medical
        """
        meta     = metadata or {}
        gender   = meta.get("gender", "general").lower()
        age      = int(meta.get("age", 40) or 40)
        history  = meta.get("medical_history", [])

        recs = {
            "cardiovascular": [],
            "nutrition":      [],
            "lifestyle":      [],
            "medical":        [],
        }

        # Build sets of detected issues for fast lookup
        abnormal_keys  = {c["param_key"] for c in classified if c["status"] != "Normal"}
        pattern_names  = {p["name"] for p in patterns}
        cv_score       = scores.get("cardiovascular", {}).get("risk_pct", 0)
        diabetes_score = scores.get("diabetes",       {}).get("risk_pct", 0)
        health_score   = scores.get("health_score",   {}).get("score", 50)

        # ── Cardiovascular ───────────────────────────────────────────────────
        if "total_cholesterol" in abnormal_keys or "ldl_cholesterol" in abnormal_keys:
            recs["cardiovascular"].append({
                "icon":  "🥑",
                "text":  "Adopt a heart-healthy diet: increase monounsaturated fats (avocado, olive oil) and reduce saturated and trans fats.",
                "linked": "High Cholesterol / LDL"
            })
        if "hdl_cholesterol" in abnormal_keys:
            recs["cardiovascular"].append({
                "icon":  "🏃",
                "text":  "Regular aerobic exercise (30 min, 5 days/week) significantly raises HDL cholesterol.",
                "linked": "Low HDL"
            })
        if "triglycerides" in abnormal_keys:
            recs["cardiovascular"].append({
                "icon":  "🍬",
                "text":  "Reduce refined carbohydrates, sugary beverages, and alcohol to lower triglycerides.",
                "linked": "High Triglycerides"
            })
        if cv_score >= 20:
            recs["cardiovascular"].append({
                "icon":  "💊",
                "text":  "Discuss statin therapy eligibility with your cardiologist given your elevated cardiovascular risk score.",
                "linked": "Cardiovascular Risk"
            })
        if "Elevated Cardiovascular Risk" in pattern_names:
            recs["cardiovascular"].append({
                "icon":  "🫀",
                "text":  "Consider a cardiology referral for a comprehensive cardiac risk evaluation including ECG and stress test.",
                "linked": "Cardiovascular Pattern"
            })

        # ── Nutrition / Diet ─────────────────────────────────────────────────
        if "hemoglobin" in abnormal_keys or "iron" in abnormal_keys or "ferritin" in abnormal_keys:
            recs["nutrition"].append({
                "icon":  "🥩",
                "text":  "Increase dietary iron: red meat, legumes, tofu, spinach, and fortified cereals. Pair with Vitamin C to enhance absorption.",
                "linked": "Anemia / Low Iron"
            })
        if "vitamin_d" in abnormal_keys:
            recs["nutrition"].append({
                "icon":  "☀️",
                "text":  "Increase sun exposure (15–20 min daily) and consume Vitamin D-rich foods: fatty fish, egg yolks, fortified dairy. Supplementation (1000–2000 IU/day) may be needed.",
                "linked": "Vitamin D Deficiency"
            })
        if "vitamin_b12" in abnormal_keys:
            recs["nutrition"].append({
                "icon":  "🥚",
                "text":  "Consume B12-rich foods: meat, fish, dairy, eggs. If vegetarian/vegan, B12 supplementation is essential.",
                "linked": "Low Vitamin B12"
            })
        if "glucose_fasting" in abnormal_keys or "hba1c" in abnormal_keys:
            recs["nutrition"].append({
                "icon":  "🥗",
                "text":  "Follow a low glycaemic index diet: whole grains, legumes, non-starchy vegetables. Avoid sugary drinks and processed foods.",
                "linked": "Blood Sugar Control"
            })
        if "uric_acid" in abnormal_keys:
            recs["nutrition"].append({
                "icon":  "🍺",
                "text":  "Limit purine-rich foods (organ meats, shellfish, red meat) and alcohol. Increase water intake to 2–3 L/day.",
                "linked": "High Uric Acid"
            })
        if "albumin" in abnormal_keys or "total_protein" in abnormal_keys:
            recs["nutrition"].append({
                "icon":  "🥜",
                "text":  "Increase protein intake: lean meats, eggs, dairy, legumes, nuts. Target 1.2–1.5 g protein per kg body weight.",
                "linked": "Low Protein"
            })
        if "magnesium" in abnormal_keys:
            recs["nutrition"].append({
                "icon":  "🥦",
                "text":  "Eat magnesium-rich foods: dark leafy greens, nuts, seeds, whole grains, and legumes.",
                "linked": "Low Magnesium"
            })

        # General healthy diet
        recs["nutrition"].append({
            "icon":  "🍎",
            "text":  "Maintain a balanced diet: at least 5 servings of fruits and vegetables daily, whole grains, and healthy fats.",
            "linked": "General Health"
        })

        # ── Lifestyle ────────────────────────────────────────────────────────
        recs["lifestyle"].append({
            "icon":  "🚶",
            "text":  "Aim for 150 minutes of moderate-intensity aerobic activity per week (brisk walking, cycling, swimming).",
            "linked": "General Health"
        })
        recs["lifestyle"].append({
            "icon":  "💧",
            "text":  "Stay well-hydrated: drink 8–10 glasses of water per day, especially important for kidney and metabolic health.",
            "linked": "Kidney / Metabolic Health"
        })
        recs["lifestyle"].append({
            "icon":  "😴",
            "text":  "Prioritize 7–9 hours of quality sleep per night. Poor sleep worsens metabolic and cardiovascular health.",
            "linked": "General Health"
        })

        if cv_score >= 15 or diabetes_score >= 20:
            recs["lifestyle"].append({
                "icon":  "🚭",
                "text":  "Avoid smoking and limit alcohol consumption (max 1 drink/day for women, 2 for men).",
                "linked": "Cardiovascular / Metabolic Risk"
            })
        if health_score < 70:
            recs["lifestyle"].append({
                "icon":  "🧘",
                "text":  "Practice stress management: mindfulness, yoga, or deep breathing exercises to reduce cortisol and improve overall health.",
                "linked": "General Wellness"
            })
        if "alt" in abnormal_keys or "ast" in abnormal_keys:
            recs["lifestyle"].append({
                "icon":  "🍷",
                "text":  "Avoid alcohol and review all medications with your doctor — some can be hepatotoxic.",
                "linked": "Liver Health"
            })

        # ── Medical Advice ───────────────────────────────────────────────────
        critical_params = [c for c in classified if c["severity"] == "critical"]
        if critical_params:
            param_names = ", ".join(c["display_name"] for c in critical_params)
            recs["medical"].append({
                "icon":  "🚨",
                "text":  f"URGENT: Critical values detected for {param_names}. Seek immediate medical evaluation.",
                "linked": "Critical Values"
            })

        if "Diabetes / Pre-diabetes Indicators" in pattern_names or diabetes_score >= 35:
            recs["medical"].append({
                "icon":  "🩺",
                "text":  "Schedule an endocrinology consultation for comprehensive diabetes evaluation and management.",
                "linked": "Diabetes Risk"
            })
        if "Kidney Stress Indicators" in pattern_names:
            recs["medical"].append({
                "icon":  "🫘",
                "text":  "Nephrology referral recommended. Repeat kidney function tests in 3 months.",
                "linked": "Kidney Stress"
            })
        if "Liver Function Abnormality" in pattern_names:
            recs["medical"].append({
                "icon":  "🫁",
                "text":  "Hepatology consultation and liver ultrasound recommended.",
                "linked": "Liver Abnormality"
            })
        if "Possible Hypothyroidism" in pattern_names or "Possible Hyperthyroidism" in pattern_names:
            recs["medical"].append({
                "icon":  "🦋",
                "text":  "Repeat thyroid function panel and endocrinology follow-up recommended.",
                "linked": "Thyroid"
            })
        if "Infection / Inflammation Markers" in pattern_names:
            recs["medical"].append({
                "icon":  "🦠",
                "text":  "Clinical evaluation to identify infection source. Blood culture or further workup may be needed.",
                "linked": "Infection"
            })

        recs["medical"].append({
            "icon":  "📅",
            "text":  "Schedule a follow-up blood test in 3–6 months to monitor changes, especially for any abnormal values.",
            "linked": "Monitoring"
        })
        recs["medical"].append({
            "icon":  "⚕️",
            "text":  "Share this full report with your primary care physician for integrated medical management.",
            "linked": "General"
        })

        # Remove duplicates
        for cat in recs:
            seen = set()
            unique = []
            for r in recs[cat]:
                if r["text"] not in seen:
                    seen.add(r["text"])
                    unique.append(r)
            recs[cat] = unique

        return recs