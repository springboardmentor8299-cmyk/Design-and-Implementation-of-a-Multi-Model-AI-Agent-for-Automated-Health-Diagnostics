def apply_context(data, risks):

    age = data.get("age")
    gender = data.get("gender")

    updated_risks = risks.copy()

    # -------- AGE BASED ADJUSTMENTS --------
    if age:

        # Cardiovascular risk increases with age
        if "Cardiovascular Risk" in updated_risks:
            if age > 50:
                updated_risks["Cardiovascular Risk"]["score"] += 10
                updated_risks["Cardiovascular Risk"]["level"] = "HIGH"

        # Diabetes risk refinement
        if "Diabetes Risk" in updated_risks:
            if age < 30:
                updated_risks["Diabetes Risk"]["score"] -= 5

    # -------- GENDER BASED ADJUSTMENTS --------
    if gender:

        gender = gender.lower()

        # Anemia more common in females
        if gender == "female" and "Anemia Risk" in updated_risks:
            updated_risks["Anemia Risk"]["score"] += 5

        # Thyroid more common in females
        if gender == "female" and "Thyroid Dysfunction Risk" in updated_risks:
            updated_risks["Thyroid Dysfunction Risk"]["score"] += 5

    return updated_risks