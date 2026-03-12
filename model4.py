def explain_risk(parameters):

    explanation = []

    for p in parameters:

        if p["status"] == "High":
            explanation.append(f"{p['name']} is very high.")

        elif p["status"] == "Medium":
            explanation.append(f"{p['name']} is slightly abnormal.")

        else:
            explanation.append(f"{p['name']} is normal.")

    return explanation