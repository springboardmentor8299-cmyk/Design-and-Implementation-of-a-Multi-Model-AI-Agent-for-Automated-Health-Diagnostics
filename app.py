from flask import Flask, render_template, request
import os

from extractor import extract_parameters
from validator import clean_data

from model1 import classify_parameters
from model2 import calculate_risk
from model3 import contextual_analysis
from model4 import explain_risk

from chart_generator import generate_chart
from pdf_report import generate_pdf

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files["file"]
    age = int(request.form["age"])
    gender = request.form["gender"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    parameters = extract_parameters(filepath)

    clean_parameters = clean_data(parameters)

    classified = classify_parameters(clean_parameters)

    contextual = contextual_analysis(classified, age, gender)

    risk = calculate_risk(contextual)

    explanation = explain_risk(contextual)

    chart_path = generate_chart(contextual)

    pdf_path = generate_pdf(contextual, risk)

    return render_template(
        "result.html",
        parameters=contextual,
        risk=risk,
        explanation=explanation,
        chart=chart_path,
        pdf=pdf_path
    )


if __name__ == "__main__":
    app.run(debug=True)