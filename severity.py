def get_severity(risks):

    severity = {}

    for risk, risk_data in risks.items():

        if isinstance(risk_data, dict):
            severity[risk] = risk_data.get("level", "LOW")
        else:
            severity[risk] = "LOW"

    return severity