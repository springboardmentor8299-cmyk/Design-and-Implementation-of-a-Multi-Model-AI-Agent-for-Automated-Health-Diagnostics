def calculate_risk(parameters):

    score = 0

    for p in parameters:

        if p["status"] == "High":
            score += 2

        elif p["status"] == "Medium":
            score += 1

    if score <= 2:
        return "Low Risk"

    elif score <= 5:
        return "Medium Risk"

    else:
        return "High Risk"