def synthesize_findings(param_results, risk_results, patterns=None):
    summary = []

    for param, status in param_results.items():
        if status == "low":
            summary.append(f"{param.capitalize()} is low.")
        elif status == "high":
            summary.append(f"{param.capitalize()} is high.")
        elif status == "borderline":
            summary.append(f"{param.capitalize()} is borderline.")

    for risk, value in risk_results.items():
        if value == "high":
            summary.append(f"High {risk.lower()} detected.")
        elif value == "moderate":
            summary.append(f"Moderate {risk.lower()} detected.")


    if patterns:
        for p in patterns:
            summary.append(f"Pattern detected: {p}")

    return " ".join(summary)