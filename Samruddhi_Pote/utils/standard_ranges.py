"""Canonical medical ranges used by Milestone 1 and 2 models."""

STANDARD_RANGES = {
    "Hemoglobin": (12.0, 15.5),
    "Glucose": (70.0, 99.0),
    "Cholesterol": (125.0, 200.0),
    "WBC": (4000.0, 11000.0),
    "Platelets": (150000.0, 450000.0),
    "LDL": (0.0, 100.0),
    "HDL": (40.0, 60.0),
    "Triglycerides": (0.0, 150.0),
    "Creatinine": (0.6, 1.3),
}

UNITS = {
    "Hemoglobin": "g/dL",
    "Glucose": "mg/dL",
    "Cholesterol": "mg/dL",
    "WBC": "cells/uL",
    "Platelets": "cells/uL",
    "LDL": "mg/dL",
    "HDL": "mg/dL",
    "Triglycerides": "mg/dL",
    "Creatinine": "mg/dL",
}

ALIASES = {
    "Total Cholesterol": "Cholesterol",
    "LDL Cholesterol": "LDL",
    "HDL Cholesterol": "HDL",
    "TG": "Triglycerides",
    "FBS": "Glucose",
    "Blood Glucose": "Glucose",
    "Serum Creatinine": "Creatinine",
    "TLC": "WBC",
    "Total Leukocyte Count": "WBC",
    "White Blood Cell Count": "WBC",
    "PLT": "Platelets",
    "Platelet Count": "Platelets",
}
