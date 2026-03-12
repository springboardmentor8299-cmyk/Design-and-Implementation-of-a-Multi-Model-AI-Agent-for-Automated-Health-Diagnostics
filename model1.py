def classify_parameters(parameters):

    for p in parameters:

        v = p["value"]

        if v < 50:
            p["status"] = "Low"

        elif 50 <= v <= 150:
            p["status"] = "Medium"

        else:
            p["status"] = "High"

    return parameters