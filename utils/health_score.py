def calculate_risk_score(risks, age, data):

    score = 100

    for r in risks:
        severity = str(r.get("severity", "")).lower()

        if severity == "high":
            score -= 25
        elif severity == "medium":
            score -= 15
        else:
            score -= 8

    if int(age) > 50:
        score -= 10

    return max(score, 0)