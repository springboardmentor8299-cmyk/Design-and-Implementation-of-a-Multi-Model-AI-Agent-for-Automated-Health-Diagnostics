import pandas as pd

def get_value(df, param):
    try:
        return float(df.loc[df["Parameter"] == param, "Value"].values[0])
    except:
        return None


def calculate_cardiovascular_risk(df):
    score = 0
    reasons = []

    ldl = get_value(df, "LDL")
    hdl = get_value(df, "HDL")
    trig = get_value(df, "Triglycerides")
    chol = get_value(df, "Cholesterol")

    if ldl and ldl > 130:
        score += 2
        reasons.append("High LDL")

    if hdl and hdl < 40:
        score += 2
        reasons.append("Low HDL")

    if trig and trig > 150:
        score += 2
        reasons.append("High Triglycerides")

    if chol and chol > 200:
        score += 2
        reasons.append("High Cholesterol")

    return classify_risk(score), score, reasons


def calculate_diabetes_risk(df):
    score = 0
    reasons = []

    glucose = get_value(df, "Glucose")

    if glucose:
        if glucose > 126:
            score += 3
            reasons.append("Very high glucose")
        elif glucose > 100:
            score += 2
            reasons.append("Elevated glucose")

    return classify_risk(score), score, reasons

def calculate_kidney_risk(df):
    score = 0
    reasons = []

    creat = get_value(df, "Creatinine")
    urea = get_value(df, "Urea")

    if creat and creat > 1.3:
        score += 3   
        reasons.append("High creatinine")

    if urea and urea > 20:
        score += 2
        reasons.append("High urea")

    return classify_risk(score), score, reasons

def calculate_anemia_risk(df):
    score = 0
    reasons = []

    hb = get_value(df, "Hemoglobin")
    rbc = get_value(df, "RBC")

    if hb and hb < 12:
        score += 2
        reasons.append("Low hemoglobin")

    if rbc and rbc < 4.2:
        score += 2
        reasons.append("Low RBC")

    return classify_risk(score), score, reasons

def classify_risk(score):
    if score >= 4:              
        return "HIGH RISK"
    elif score >= 2:            
        return "MODERATE RISK"
    else:
        return "LOW RISK"


def analyze_risk(df):

    results = {}

    funcs = {
        "Cardiovascular Risk": calculate_cardiovascular_risk,
        "Diabetes Risk": calculate_diabetes_risk,
        "Kidney Risk": calculate_kidney_risk,
        "Anemia Risk": calculate_anemia_risk
    }

    for key, func in funcs.items():
        label, score, reasons = func(df)

        results[key] = {
            "level": label,
            "score": score,
            "reasons": reasons
        }

    return results