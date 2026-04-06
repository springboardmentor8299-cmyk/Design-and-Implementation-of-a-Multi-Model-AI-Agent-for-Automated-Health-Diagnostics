ranges = {
    "Hemoglobin": (13, 17),
    "Glucose": (70, 100),
    "Cholesterol": (125, 200),
    "Triglycerides": (0, 150),
    "HDL": (40, 60),
    "LDL": (0, 130),
    "WBC": (4000, 11000),
    "RBC": (4.5, 5.9),
    "Platelets": (150000, 450000)
}


def interpret(data):

    results = {}

    for param, value in data.items():

        if param in ranges:
            low, high = ranges[param]

            # 🔥 Determine status
            if value < low:
                status = "Low"
            elif value > high:
                status = "High"
            else:
                status = "Normal"

            # 🔥 Severity (NEW - important)
            if status == "High":
                if value > high * 1.3:
                    severity = "Critical"
                else:
                    severity = "Moderate"

            elif status == "Low":
                if value < low * 0.7:
                    severity = "Critical"
                else:
                    severity = "Moderate"
            else:
                severity = "Normal"

            # 🔥 Store structured output
            results[param] = {
                "value": value,
                "status": status,
                "severity": severity,
                "range": {
                    "low": low,
                    "high": high
                }
            }

    return results