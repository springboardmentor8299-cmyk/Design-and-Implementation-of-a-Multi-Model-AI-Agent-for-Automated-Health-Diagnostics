from flask import Flask, render_template, request
import os
from extractor import run_extraction
from model1 import interpret_parameters

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def home():

    extracted = None
    analysis = None

    if request.method == "POST":

        file = request.files["file"]

        if file:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

            extracted = run_extraction(path, "WEB001")
            analysis = interpret_parameters(extracted)

    return render_template("index.html",
                           extracted=extracted,
                           analysis=analysis)


if __name__ == "__main__":
    app.run(debug=True)
