"""Definitions for common medical blood test panels.

This acts as a lightweight knowledge base that maps a panel name to the
parameters typically included in that panel.
"""

TEST_PANELS = {
    "CBC": [
        "Hemoglobin",
        "WBC",
        "Platelets",
    ],
    "Lipid Profile": [
        "Cholesterol",
        "HDL",
        "LDL",
        "Triglycerides",
    ],
    "Blood Sugar": [
        "Glucose",
    ],
    "Kidney Function": [
        "Creatinine",
    ],
}

