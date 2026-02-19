import re


def extract_parameters(text):

    patterns = {

        "Hemoglobin": r"(Hemoglobin|Hb)\s*\(?[g/dL]*\)?\s*[:\-]?\s*(\d+\.?\d*)",

        "WBC": r"(WBC|WBCs|Leukocyte Count)\s*\(?[a-zA-Z/]*\)?\s*[:\-]?\s*(\d+\.?\d*)",

        "RBC": r"(RBC|RBCs)\s*\(?[a-zA-Z/]*\)?\s*[:\-]?\s*(\d+\.?\d*)",

        "Platelets": r"(Platelets|Platelet Count)\s*\(?[a-zA-Z/]*\)?\s*[:\-]?\s*(\d+\.?\d*)",

        "Glucose": r"(Glucose)\s*\(?[a-zA-Z/]*\)?\s*[:\-]?\s*(\d+\.?\d*)",

        "Cholesterol": r"(Cholesterol)\s*\(?[a-zA-Z/]*\)?\s*[:\-]?\s*(\d+\.?\d*)"

    }

    extracted = {}

    for parameter, pattern in patterns.items():

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            value = match.group(2)

            extracted[parameter] = {

                "value": float(value),

                "unit": ""

            }

    return extracted
