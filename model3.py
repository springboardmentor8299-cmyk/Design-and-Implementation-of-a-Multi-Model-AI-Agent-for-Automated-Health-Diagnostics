def contextual_analysis(parameters, age, gender):

    for p in parameters:

        if age > 50 and p["status"] == "Medium":
            p["status"] = "High"

    return parameters