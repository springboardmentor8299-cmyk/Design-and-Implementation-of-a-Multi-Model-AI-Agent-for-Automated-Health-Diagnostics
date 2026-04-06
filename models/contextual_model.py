def contextual_analysis(findings, age=None, gender=None, lifestyle=None):

    context = []

    # 🔥 AGE-BASED CONTEXT
    try:
        age = int(age) if age else None
    except:
        age = None

    if age:
        if age > 50:
            context.append("Age above 50 increases risk for cardiovascular and metabolic diseases.")
        elif age < 18:
            context.append("Young age group - most parameters should be within optimal range.")

    # 🔥 GENDER-BASED CONTEXT
    if gender:
        gender = gender.lower()

        if gender == "male":
            context.append("Males generally have higher cardiovascular risk compared to females.")

        elif gender == "female":
            context.append("Hormonal factors in females can influence cholesterol and iron levels.")

    # 🔥 RISK-BASED CONTEXT
    for risk in findings:
        name = risk.get("name", "").lower()

        if "cardio" in name or "heart" in name:
            context.append("Cardiovascular risk detected based on lipid profile and lifestyle factors.")

        if "diabetes" in name:
            context.append("Elevated glucose levels may indicate risk of diabetes.")

        if "anemia" in name:
            context.append("Low hemoglobin may indicate anemia.")

    # 🔥 LIFESTYLE CONTEXT (VERY IMPORTANT)
    if lifestyle:
        if lifestyle.get("smoking", "").lower() == "yes":
            context.append("Smoking significantly increases cardiovascular and lung disease risk.")

        if lifestyle.get("exercise", "").lower() in ["no", "low"]:
            context.append("Low physical activity contributes to multiple health risks.")

        if lifestyle.get("sleep", "").lower() in ["poor", "low"]:
            context.append("Poor sleep quality can affect metabolism and overall health.")

        if lifestyle.get("alcohol", "").lower() == "yes":
            context.append("Alcohol consumption can impact liver and metabolic health.")

    # 🔥 Remove duplicates
    context = list(set(context))

    return context