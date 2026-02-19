import pandas as pd
import re

def extract_parameters_from_text(text):

    # Convert to lowercase for flexible matching
    text = text.lower()

    data = []

    patterns = {

        "Hemoglobin": r"hemo\w*\s*\(?g/dl\)?\s*(\d+\.?\d*)",

        "RBC": r"rbc\s*(\d+\.?\d*)",

        "WBC": r"wbc\s*(\d+\.?\d*)",

        "Platelets": r"platelets\s*(\d+\.?\d*)",

        "Glucose": r"glucose\s*(\d+\.?\d*)",

        "Cholesterol": r"cholesterol\s*(\d+\.?\d*)",

        "HDL": r"hdl\s*(\d+\.?\d*)",

        "LDL": r"ldl\s*(\d+\.?\d*)",

        "Triglycerides": r"triglycerides\s*(\d+\.?\d*)",

        "Total Bilirubin": r"total bilirubin\s*(\d+\.?\d*)",

        "SGOT": r"sgot\s*(\d+\.?\d*)",

        "SGPT": r"sgpt\s*(\d+\.?\d*)",

        "Creatinine": r"creatinine\s*(\d+\.?\d*)",

        "Urea": r"urea\s*(\d+\.?\d*)"

    }

    for parameter, pattern in patterns.items():

        match = re.search(pattern, text)

        if match:

            value = float(match.group(1))

            data.append({

                "Parameter": parameter,

                "Value": value

            })

    df = pd.DataFrame(data)

    return df
