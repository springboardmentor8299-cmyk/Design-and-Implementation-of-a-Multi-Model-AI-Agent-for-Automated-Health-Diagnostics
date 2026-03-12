import pandas as pd


def calculate_cardiovascular_risk(df):

    score = 0

    try:

        ldl = df.loc[df["Parameter"]=="LDL","Value"].values[0]
        hdl = df.loc[df["Parameter"]=="HDL","Value"].values[0]
        trig = df.loc[df["Parameter"]=="Triglycerides","Value"].values[0]
        chol = df.loc[df["Parameter"]=="Cholesterol","Value"].values[0]

        if ldl > 130:
            score += 2

        if hdl < 40:
            score += 2

        if trig > 150:
            score += 2

        if chol > 200:
            score += 2

    except:
        pass


    if score >= 6:
        return "HIGH RISK"

    elif score >=3:
        return "MODERATE RISK"

    else:
        return "LOW RISK"



def calculate_diabetes_risk(df):

    score = 0

    try:

        glucose = df.loc[df["Parameter"]=="Glucose","Value"].values[0]

        if glucose > 126:
            score += 3

        elif glucose > 100:
            score += 2

    except:
        pass


    if score >=3:
        return "HIGH RISK"

    elif score >=2:
        return "MODERATE RISK"

    else:
        return "LOW RISK"



def calculate_kidney_risk(df):

    score = 0

    try:

        creat = df.loc[df["Parameter"]=="Creatinine","Value"].values[0]
        urea = df.loc[df["Parameter"]=="Urea","Value"].values[0]

        if creat > 1.3:
            score += 2

        if urea > 20:
            score += 2

    except:
        pass


    if score >=4:
        return "HIGH RISK"

    elif score >=2:
        return "MODERATE RISK"

    else:
        return "LOW RISK"



def calculate_anemia_risk(df):

    score = 0

    try:

        hb = df.loc[df["Parameter"]=="Hemoglobin","Value"].values[0]
        rbc = df.loc[df["Parameter"]=="RBC","Value"].values[0]

        if hb < 12:
            score += 2

        if rbc < 4.2:
            score += 2

    except:
        pass


    if score >=4:
        return "HIGH RISK"

    elif score >=2:
        return "MODERATE RISK"

    else:
        return "LOW RISK"



def analyze_risk(df):

    return {

        "Cardiovascular Risk":
        calculate_cardiovascular_risk(df),

        "Diabetes Risk":
        calculate_diabetes_risk(df),

        "Kidney Risk":
        calculate_kidney_risk(df),

        "Anemia Risk":
        calculate_anemia_risk(df)

    }