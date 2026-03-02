"""
Model 1: Parameter Interpretation Module
Analyzes extracted blood parameters and provides health insights
"""

def interpret_parameters(parameters: dict) -> dict:
    """Interpret blood test parameters and provide analysis"""
    
    if not parameters:
        return {"error": "No parameters to analyze"}
    
    # Reference ranges
    RANGES = {
        "hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
        "wbc_count": {"min": 4.5, "max": 11.0, "unit": "x10^3/uL"},
        "platelet_count": {"min": 150, "max": 450, "unit": "x10^3/uL"},
        "fasting_plasma_glucose": {"min": 70, "max": 99, "unit": "mg/dL"},
        "hba1c": {"min": 4.0, "max": 5.6, "unit": "%"},
        "total_cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
        "hdl_cholesterol": {"min": 40, "max": 999, "unit": "mg/dL"},
        "ldl_cholesterol": {"min": 0, "max": 100, "unit": "mg/dL"},
        "triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
        "creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
        "urea": {"min": 7, "max": 20, "unit": "mg/dL"},
        "sgot": {"min": 0, "max": 40, "unit": "U/L"},
        "sgpt": {"min": 0, "max": 41, "unit": "U/L"},
    }
    
    analysis = {
        "patient_info": {},
        "results": [],
        "summary": {"normal": 0, "abnormal": 0}
    }
    
    # Extract patient info
    if parameters.get("patient_name"):
        analysis["patient_info"]["name"] = parameters["patient_name"]
    if parameters.get("age"):
        analysis["patient_info"]["age"] = parameters["age"]
    if parameters.get("gender"):
        analysis["patient_info"]["gender"] = parameters["gender"]
    
    # Analyze each parameter
    for param, value in parameters.items():
        if param in ["patient_name", "age", "gender"] or value is None:
            continue
        
        if param in RANGES:
            ref = RANGES[param]
            status = "Normal"
            
            if value < ref["min"]:
                status = "Low"
                analysis["summary"]["abnormal"] += 1
            elif value > ref["max"]:
                status = "High"
                analysis["summary"]["abnormal"] += 1
            else:
                analysis["summary"]["normal"] += 1
            
            analysis["results"].append({
                "parameter": param.replace("_", " ").title(),
                "value": value,
                "unit": ref["unit"],
                "range": f"{ref['min']} - {ref['max']}",
                "status": status
            })
    
    return analysis
