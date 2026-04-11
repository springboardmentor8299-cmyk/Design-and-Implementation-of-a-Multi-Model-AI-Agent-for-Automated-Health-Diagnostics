def generate_recommendations(risks, data=None):

    recs = []

    age = None
    gender = None

    if data:
        age = data.get("age")
        gender = data.get("gender")

    # -------- DIABETES --------
    if "Diabetes Risk" in risks:

        if age and age < 30:
            recs.append(
                "Your diabetes risk is concerning for your age. Reduce sugar intake immediately and maintain an active lifestyle."
            )
        else:
            recs.append(
                "Maintain a low-sugar and low-carbohydrate diet, monitor blood glucose levels regularly, and exercise daily."
            )

    # -------- HEART --------
    if "Cardiovascular Risk" in risks:

        if age and age > 45:
            recs.append(
                "Due to your age and cholesterol levels, regular heart checkups and strict diet control are highly recommended."
            )
        else:
            recs.append(
                "Reduce oily foods, increase physical activity, and maintain a heart-healthy diet."
            )

    # -------- ANEMIA --------
    if "Anemia Risk" in risks:

        if gender == "female":
            recs.append(
                "Increase iron-rich foods like spinach and dates. Women are more prone to anemia, so regular monitoring is advised."
            )
        else:
            recs.append(
                "Include iron-rich foods and consult a doctor if symptoms persist."
            )

    # -------- THYROID --------
    if "Thyroid Dysfunction Risk" in risks:

        if gender == "female":
            recs.append(
                "Thyroid issues are common in females. Consult an endocrinologist and monitor hormone levels regularly."
            )
        else:
            recs.append(
                "Maintain a balanced diet and consult a doctor for thyroid evaluation."
            )

    # -------- GENERAL --------
    if risks:
        recs.append(
            "Consult a healthcare professional for a detailed evaluation and personalized treatment plan."
        )

    return recs