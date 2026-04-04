from fastapi import FastAPI
import pandas as pd
from api.medical_api import fetch_reference_ranges
from processing.comparator import compare_with_ranges

app = FastAPI()

@app.post("/analyze")
def analyze(data: dict):

    df = pd.DataFrame(data["parameters"])

    df = compare_with_ranges(df, fetch_reference_ranges())


    return df.to_dict(orient="records") 