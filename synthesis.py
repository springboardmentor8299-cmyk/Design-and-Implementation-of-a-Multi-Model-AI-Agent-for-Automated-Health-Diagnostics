def synthesize_findings(analysis, risks):

    summary = []

    # -------- INTRO --------
    summary.append("Your blood report analysis shows some important health observations:")

    # -------- PARAMETER LEVEL --------
    for param, info in analysis.items():

        if info["status"] != "NORMAL":

            readable_param = param.replace("_", " ").title()

            if info["status"] == "HIGH":
                summary.append(f"{readable_param} is higher than the normal range.")

            elif info["status"] == "LOW":
                summary.append(f"{readable_param} is lower than the normal range.")

    # -------- RISK LEVEL --------
    if risks:
        summary.append("\nBased on the above values, the following health risks are identified:")

        for risk, info in risks.items():
            if isinstance(info, dict):
                summary.append(f"{risk} (Severity: {info.get('level')}, Score: {info.get('score')})")
            else:
                summary.append(f"{risk}")

    # -------- FINAL INSIGHT --------
    # -------- FINAL INSIGHT (FIXED) --------

    abnormal_params = [
        p for p, info in analysis.items() if info["status"] != "NORMAL"
    ]

    if abnormal_params:
        summary.append("Overall, some parameters are outside the normal range and require attention.")
    else:
        summary = ["Your blood report appears normal. All parameters are within the healthy range."]

    return summary