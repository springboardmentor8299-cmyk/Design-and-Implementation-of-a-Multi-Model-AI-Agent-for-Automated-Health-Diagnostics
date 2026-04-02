# backend/reference_ranges.py
# Comprehensive medical reference ranges for common blood test parameters

REFERENCE_RANGES = {
    # ── Complete Blood Count (CBC) ──────────────────────────────────────────
    "hemoglobin": {
        "display_name": "Hemoglobin",
        "category": "CBC",
        "male":    {"min": 13.5, "max": 17.5, "unit": "g/dL"},
        "female":  {"min": 12.0, "max": 15.5, "unit": "g/dL"},
        "general": {"min": 12.0, "max": 17.5, "unit": "g/dL"},
    },
    "hematocrit": {
        "display_name": "Hematocrit",
        "category": "CBC",
        "male":    {"min": 41.0, "max": 53.0, "unit": "%"},
        "female":  {"min": 36.0, "max": 46.0, "unit": "%"},
        "general": {"min": 36.0, "max": 53.0, "unit": "%"},
    },
    "rbc": {
        "display_name": "Red Blood Cells (RBC)",
        "category": "CBC",
        "male":    {"min": 4.5,  "max": 5.9,  "unit": "million/µL"},
        "female":  {"min": 4.1,  "max": 5.1,  "unit": "million/µL"},
        "general": {"min": 4.1,  "max": 5.9,  "unit": "million/µL"},
    },
    "wbc": {
        "display_name": "White Blood Cells (WBC)",
        "category": "CBC",
        "general": {"min": 4.5,  "max": 11.0, "unit": "thousand/µL"},
    },
    "platelets": {
        "display_name": "Platelets",
        "category": "CBC",
        "general": {"min": 150.0,"max": 400.0,"unit": "thousand/µL"},
    },
    "mcv": {
        "display_name": "Mean Corpuscular Volume (MCV)",
        "category": "CBC",
        "general": {"min": 80.0, "max": 100.0,"unit": "fL"},
    },
    "mch": {
        "display_name": "Mean Corpuscular Hemoglobin (MCH)",
        "category": "CBC",
        "general": {"min": 27.0, "max": 33.0, "unit": "pg"},
    },
    "mchc": {
        "display_name": "Mean Corpuscular Hemoglobin Concentration (MCHC)",
        "category": "CBC",
        "general": {"min": 31.0, "max": 37.0, "unit": "g/dL"},
    },

    # ── Lipid Panel ─────────────────────────────────────────────────────────
    "total_cholesterol": {
        "display_name": "Total Cholesterol",
        "category": "Lipid Panel",
        "general": {"min": 0,    "max": 200.0,"unit": "mg/dL"},
    },
    "ldl_cholesterol": {
        "display_name": "LDL Cholesterol",
        "category": "Lipid Panel",
        "general": {"min": 0,    "max": 100.0,"unit": "mg/dL"},
    },
    "hdl_cholesterol": {
        "display_name": "HDL Cholesterol",
        "category": "Lipid Panel",
        "male":    {"min": 40.0, "max": 999,  "unit": "mg/dL"},
        "female":  {"min": 50.0, "max": 999,  "unit": "mg/dL"},
        "general": {"min": 40.0, "max": 999,  "unit": "mg/dL"},
    },
    "triglycerides": {
        "display_name": "Triglycerides",
        "category": "Lipid Panel",
        "general": {"min": 0,    "max": 150.0,"unit": "mg/dL"},
    },
    "vldl": {
        "display_name": "VLDL Cholesterol",
        "category": "Lipid Panel",
        "general": {"min": 2.0,  "max": 30.0, "unit": "mg/dL"},
    },

    # ── Blood Sugar ──────────────────────────────────────────────────────────
    "glucose_fasting": {
        "display_name": "Fasting Glucose",
        "category": "Blood Sugar",
        "general": {"min": 70.0, "max": 100.0,"unit": "mg/dL"},
    },
    "glucose": {
        "display_name": "Glucose",
        "category": "Blood Sugar",
        "general": {"min": 70.0, "max": 140.0,"unit": "mg/dL"},
    },
    "hba1c": {
        "display_name": "HbA1c (Glycated Hemoglobin)",
        "category": "Blood Sugar",
        "general": {"min": 0,    "max": 5.7,  "unit": "%"},
    },
    "insulin": {
        "display_name": "Fasting Insulin",
        "category": "Blood Sugar",
        "general": {"min": 2.0,  "max": 25.0, "unit": "µIU/mL"},
    },

    # ── Kidney Function ──────────────────────────────────────────────────────
    "creatinine": {
        "display_name": "Creatinine",
        "category": "Kidney Function",
        "male":    {"min": 0.74, "max": 1.35, "unit": "mg/dL"},
        "female":  {"min": 0.59, "max": 1.04, "unit": "mg/dL"},
        "general": {"min": 0.59, "max": 1.35, "unit": "mg/dL"},
    },
    "bun": {
        "display_name": "Blood Urea Nitrogen (BUN)",
        "category": "Kidney Function",
        "general": {"min": 7.0,  "max": 25.0, "unit": "mg/dL"},
    },
    "uric_acid": {
        "display_name": "Uric Acid",
        "category": "Kidney Function",
        "male":    {"min": 3.4,  "max": 7.0,  "unit": "mg/dL"},
        "female":  {"min": 2.4,  "max": 6.0,  "unit": "mg/dL"},
        "general": {"min": 2.4,  "max": 7.0,  "unit": "mg/dL"},
    },
    "egfr": {
        "display_name": "eGFR (Estimated Glomerular Filtration Rate)",
        "category": "Kidney Function",
        "general": {"min": 60.0, "max": 999,  "unit": "mL/min/1.73m²"},
    },

    # ── Liver Function ───────────────────────────────────────────────────────
    "alt": {
        "display_name": "ALT (Alanine Aminotransferase)",
        "category": "Liver Function",
        "male":    {"min": 7.0,  "max": 56.0, "unit": "U/L"},
        "female":  {"min": 7.0,  "max": 45.0, "unit": "U/L"},
        "general": {"min": 7.0,  "max": 56.0, "unit": "U/L"},
    },
    "ast": {
        "display_name": "AST (Aspartate Aminotransferase)",
        "category": "Liver Function",
        "general": {"min": 10.0, "max": 40.0, "unit": "U/L"},
    },
    "alkaline_phosphatase": {
        "display_name": "Alkaline Phosphatase (ALP)",
        "category": "Liver Function",
        "general": {"min": 44.0, "max": 147.0,"unit": "U/L"},
    },
    "bilirubin_total": {
        "display_name": "Bilirubin (Total)",
        "category": "Liver Function",
        "general": {"min": 0.1,  "max": 1.2,  "unit": "mg/dL"},
    },
    "bilirubin_direct": {
        "display_name": "Bilirubin (Direct)",
        "category": "Liver Function",
        "general": {"min": 0.0,  "max": 0.3,  "unit": "mg/dL"},
    },
    "albumin": {
        "display_name": "Albumin",
        "category": "Liver Function",
        "general": {"min": 3.4,  "max": 5.4,  "unit": "g/dL"},
    },
    "total_protein": {
        "display_name": "Total Protein",
        "category": "Liver Function",
        "general": {"min": 6.0,  "max": 8.3,  "unit": "g/dL"},
    },

    # ── Thyroid Function ─────────────────────────────────────────────────────
    "tsh": {
        "display_name": "TSH (Thyroid Stimulating Hormone)",
        "category": "Thyroid",
        "general": {"min": 0.4,  "max": 4.0,  "unit": "mIU/L"},
    },
    "t3": {
        "display_name": "T3 (Triiodothyronine)",
        "category": "Thyroid",
        "general": {"min": 80.0, "max": 200.0,"unit": "ng/dL"},
    },
    "t4": {
        "display_name": "T4 (Thyroxine)",
        "category": "Thyroid",
        "general": {"min": 5.0,  "max": 12.0, "unit": "µg/dL"},
    },
    "free_t3": {
        "display_name": "Free T3",
        "category": "Thyroid",
        "general": {"min": 2.3,  "max": 4.1,  "unit": "pg/mL"},
    },
    "free_t4": {
        "display_name": "Free T4",
        "category": "Thyroid",
        "general": {"min": 0.8,  "max": 1.8,  "unit": "ng/dL"},
    },

    # ── Electrolytes ─────────────────────────────────────────────────────────
    "sodium": {
        "display_name": "Sodium",
        "category": "Electrolytes",
        "general": {"min": 136.0,"max": 145.0,"unit": "mEq/L"},
    },
    "potassium": {
        "display_name": "Potassium",
        "category": "Electrolytes",
        "general": {"min": 3.5,  "max": 5.0,  "unit": "mEq/L"},
    },
    "calcium": {
        "display_name": "Calcium",
        "category": "Electrolytes",
        "general": {"min": 8.5,  "max": 10.5, "unit": "mg/dL"},
    },
    "chloride": {
        "display_name": "Chloride",
        "category": "Electrolytes",
        "general": {"min": 98.0, "max": 106.0,"unit": "mEq/L"},
    },
    "bicarbonate": {
        "display_name": "Bicarbonate (CO2)",
        "category": "Electrolytes",
        "general": {"min": 22.0, "max": 29.0, "unit": "mEq/L"},
    },
    "magnesium": {
        "display_name": "Magnesium",
        "category": "Electrolytes",
        "general": {"min": 1.7,  "max": 2.2,  "unit": "mg/dL"},
    },

    # ── Iron Studies ─────────────────────────────────────────────────────────
    "iron": {
        "display_name": "Serum Iron",
        "category": "Iron Studies",
        "male":    {"min": 60.0, "max": 170.0,"unit": "µg/dL"},
        "female":  {"min": 50.0, "max": 170.0,"unit": "µg/dL"},
        "general": {"min": 50.0, "max": 170.0,"unit": "µg/dL"},
    },
    "ferritin": {
        "display_name": "Ferritin",
        "category": "Iron Studies",
        "male":    {"min": 24.0, "max": 336.0,"unit": "ng/mL"},
        "female":  {"min": 11.0, "max": 307.0,"unit": "ng/mL"},
        "general": {"min": 11.0, "max": 336.0,"unit": "ng/mL"},
    },
    "tibc": {
        "display_name": "Total Iron Binding Capacity (TIBC)",
        "category": "Iron Studies",
        "general": {"min": 250.0,"max": 370.0,"unit": "µg/dL"},
    },

    # ── Cardiac Markers ──────────────────────────────────────────────────────
    "crp": {
        "display_name": "C-Reactive Protein (CRP)",
        "category": "Cardiac/Inflammation",
        "general": {"min": 0.0,  "max": 10.0, "unit": "mg/L"},
    },
    "hs_crp": {
        "display_name": "High-Sensitivity CRP (hs-CRP)",
        "category": "Cardiac/Inflammation",
        "general": {"min": 0.0,  "max": 3.0,  "unit": "mg/L"},
    },
    "troponin_i": {
        "display_name": "Troponin I",
        "category": "Cardiac/Inflammation",
        "general": {"min": 0.0,  "max": 0.04, "unit": "ng/mL"},
    },

    # ── Vitamins & Minerals ──────────────────────────────────────────────────
    "vitamin_d": {
        "display_name": "Vitamin D (25-OH)",
        "category": "Vitamins",
        "general": {"min": 30.0, "max": 100.0,"unit": "ng/mL"},
    },
    "vitamin_b12": {
        "display_name": "Vitamin B12",
        "category": "Vitamins",
        "general": {"min": 200.0,"max": 900.0,"unit": "pg/mL"},
    },
    "folate": {
        "display_name": "Folate (Folic Acid)",
        "category": "Vitamins",
        "general": {"min": 2.7,  "max": 17.0, "unit": "ng/mL"},
    },

    # ── Hormones ─────────────────────────────────────────────────────────────
    "cortisol": {
        "display_name": "Cortisol (Morning)",
        "category": "Hormones",
        "general": {"min": 6.0,  "max": 23.0, "unit": "µg/dL"},
    },
    "testosterone": {
        "display_name": "Total Testosterone",
        "category": "Hormones",
        "male":    {"min": 300.0,"max": 1000.0,"unit": "ng/dL"},
        "female":  {"min": 15.0, "max": 70.0, "unit": "ng/dL"},
        "general": {"min": 15.0, "max": 1000.0,"unit": "ng/dL"},
    },
}


CRITICAL_THRESHOLDS = {
    "hemoglobin":       {"critical_low": 7.0,   "critical_high": 20.0},
    "glucose_fasting":  {"critical_low": 50.0,  "critical_high": 400.0},
    "glucose":          {"critical_low": 50.0,  "critical_high": 500.0},
    "potassium":        {"critical_low": 2.5,   "critical_high": 6.5},
    "sodium":           {"critical_low": 120.0, "critical_high": 160.0},
    "calcium":          {"critical_low": 6.0,   "critical_high": 13.0},
    "platelets":        {"critical_low": 50.0,  "critical_high": 1000.0},
    "creatinine":       {"critical_low": None,  "critical_high": 10.0},
    "total_cholesterol":{"critical_low": None,  "critical_high": 300.0},
    "troponin_i":       {"critical_low": None,  "critical_high": 1.0},
}


SAMPLE_REPORT = {
    "patient_name": "John Doe",
    "age": 45,
    "gender": "male",
    "hemoglobin": 13.2,
    "rbc": 4.3,
    "wbc": 9.8,
    "platelets": 180,
    "hematocrit": 40,
    "mcv": 78,
    "total_cholesterol": 230,
    "ldl_cholesterol": 155,
    "hdl_cholesterol": 38,
    "triglycerides": 190,
    "glucose_fasting": 112,
    "hba1c": 6.1,
    "creatinine": 1.1,
    "bun": 20,
    "alt": 52,
    "ast": 38,
    "bilirubin_total": 0.9,
    "albumin": 4.1,
    "tsh": 3.5,
    "sodium": 139,
    "potassium": 4.1,
    "calcium": 9.2,
    "vitamin_d": 22,
    "vitamin_b12": 350,
    "crp": 8.5,
}