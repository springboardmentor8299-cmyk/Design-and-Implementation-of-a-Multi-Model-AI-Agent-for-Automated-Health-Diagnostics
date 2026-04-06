def generate_recommendations(risks, lifestyle):

    recommendations = []

    for r in risks:
        name = str(r.get("name", "")).lower()

        if "diabetes" in name:
            recommendations.append("Reduce sugar intake and exercise daily,Lowering sugar intake prevents dangerous glucose spikes while daily exercise helps your muscles use that sugar for energy more efficiently. Together, these habits significantly improve your metabolic health and insulin sensitivity.")

        elif "heart" in name:
            recommendations.append("Avoid oily foods and do cardio exercise,Avoiding oily, fried foods reduces the intake of harmful fats that clog your arteries. Incorporating cardio exercises like running or swimming further strengthens the heart and helps maintain healthy circulation.")

        elif "anemia" in name:
            recommendations.append("Eat iron-rich foods like spinach and dates,To combat anemia, focus on eating iron-rich foods like spinach, dates, and lentils. These nutrients help your body produce more hemoglobin, effectively restoring your energy levels and reducing fatigue.")

        elif "infection" in name:
            recommendations.append("Drink fluids and maintain hygiene,Staying well-hydrated flushes toxins from your system, while maintaining good hygiene prevents the entry of germs. These simple practices are your first line of defense against common illnesses and infections.")

    # Lifestyle
    if str(lifestyle.get("exercise", "")).lower() == "no":
        recommendations.append("Start daily exercise.")

    if str(lifestyle.get("smoking", "")).lower() == "yes":
        recommendations.append("Quit smoking immediately.")

    if str(lifestyle.get("sleep", "")).lower() == "poor":
        recommendations.append("Improve sleep habits.")

    return list(set(recommendations))