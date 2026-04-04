def generate_recommendations(param_results, risk_results, user_context=None):
    recs = {
        "diet": [],
        "lifestyle": [],
        "medical": []
    }

    if param_results.get("hemoglobin") == "low":
        recs["diet"].append("Increase iron-rich foods like spinach and dates.")
        recs["medical"].append("Consult doctor for iron supplements.")

    if param_results.get("glucose") == "high":
        recs["diet"].append("Reduce sugar intake.")
        recs["lifestyle"].append("Exercise daily (30 mins).")

    if param_results.get("cholesterol") in ["high", "borderline"]:
        recs["diet"].append("Follow a low-fat diet.")
        recs["lifestyle"].append("Avoid sedentary habits.")

    
    if risk_results.get("Cardiovascular Risk") == "high":
        recs["medical"].append("Immediate cardiac consultation recommended.")

  
    if user_context:
        age = user_context.get("age", 0)
        if age < 30:
            recs["lifestyle"].append("Maintain preventive health habits early.")

    return recs