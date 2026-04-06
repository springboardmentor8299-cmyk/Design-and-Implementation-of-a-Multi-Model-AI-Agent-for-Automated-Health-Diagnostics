def explain_risk(risks):

    explanations = []

    # ✅ No risk case
    if not risks:
        return ["No major risks detected. Your health parameters appear to be within normal range."]

    for r in risks:

        name = r.get("name", "")
        level = r.get("level", "moderate").lower()

        # 🔥 Dynamic explanation based on risk type
        if name.lower() == "anemia":
            msg = "Low hemoglobin levels suggest anemia, which may cause fatigue and weakness."

        elif name.lower() == "diabetes":
            msg = "Elevated blood glucose levels indicate a potential risk of diabetes."

        elif name.lower() in ["heart disease", "cardiovascular"]:
            msg = "Abnormal cholesterol levels may increase the risk of heart disease."

        elif name.lower() == "infection":
            msg = "Elevated white blood cell count may indicate an infection or inflammation."

        elif name.lower() == "clot risk":
            msg = "High platelet levels may increase the risk of blood clotting issues."

        elif name.lower() == "liver":
            msg = "Abnormal liver-related parameters may indicate liver stress or damage."

        elif name.lower() == "kidney":
            msg = "Irregular kidney markers may suggest reduced kidney function."

        else:
            msg = f"{name} risk detected based on your health parameters."

        # 🔥 Add severity context
        if level == "high":
            msg += " This risk is high and should be addressed promptly."
        elif level == "moderate":
            msg += " This risk is moderate and should be monitored."
        else:
            msg += " This risk is currently low but maintaining healthy habits is important."

        explanations.append(msg)

    return explanations