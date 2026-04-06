from flask import Flask, render_template, request, redirect, session, send_file
import os
import sqlite3
import json
from werkzeug.utils import secure_filename

# ✅ YOUR MODULES
from utils.extraction import extract_text, extract_parameters
from utils.health_score import calculate_risk_score
from utils.validation import detect_risks
from utils.recommendation import generate_recommendations
from utils.synthesis import generate_explanations

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "secret123"

app.config["UPLOAD_FOLDER"] = "uploads"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("INSERT INTO users(username,password) VALUES (?,?)",
                    (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- ANALYZE ----------------
@app.route("/analyze", methods=["POST"])
def analyze():

    if "user" not in session:
        return redirect("/login")

    file = request.files["file"]
    filename = secure_filename(file.filename)

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    name = request.form.get("patient_name")
    age = request.form.get("age")
    gender = request.form.get("gender")

    # 🔍 OCR
    text = extract_text(filepath)

    # 🧪 Parameters
    data = extract_parameters(text)

    # ⚠ Risks
    risks = detect_risks(data)

    # 🧠 Lifestyle
    lifestyle = {
        "exercise": request.form.get("exercise"),
        "smoking": request.form.get("smoking"),
        "sleep": request.form.get("sleep")
    }

    # 📊 Score
    score = calculate_risk_score(risks, age, data)

    # 💡 Recommendations
    recommendations = generate_recommendations(risks, lifestyle)

    # 📘 Explanation
    explanations = generate_explanations(data)

    # ✅ STORE SESSION (IMPORTANT FIX)
    session["data"] = data
    session["score"] = score
    session["risks"] = risks
    session["recommendations"] = recommendations
    session["explanations"] = explanations

    # 💾 SAVE DB
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO reports(username,score,data) VALUES (?,?,?)",
                (session["user"], score, json.dumps(data)))

    conn.commit()
    conn.close()

    return render_template("result.html",
                           score=score,
                           data=data,
                           risks=risks,
                           explanations=explanations,
                           recommendations=recommendations,
                           patient_name=name,
                           age=age,
                           gender=gender)

# ---------------- CHATBOT ----------------
@app.route("/chat", methods=["POST"])
def chat():

    question = request.json.get("question", "").lower()
    data = session.get("data", {})

    answer = "Please consult a doctor for detailed advice.any other question about your diet ask me any time"

    if "my glucose level" in question:
        val = data.get("Glucose", 0)
        answer = f"Your glucose is {'high' if val > 140 else 'normal'} ({val})"

    elif "my cholesterol level" in question:
        val = data.get("Cholesterol", 0)
        answer = f"Your cholesterol is {'high' if val > 200 else 'normal'} ({val})"

    elif "diet" in question:
        answer = "Eat fruits, vegetables, and reduce junk food."

    elif "exercise" in question:
        answer = "Do at least 30 minutes of walking daily."
    elif "summary" in question:
        answer = "your report summary is given below 1:Diabetes RiskHigh glucose level 80% ,2:heart risk 50%,and anemia ,infection are dectedted risk follow the recoomendation given above"

    return {"answer": answer}

# ---------------- DOWNLOAD PDF ----------------
@app.route("/download")
def download():

    file_path = "report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    # 🔷 HEADER
    content.append(Paragraph("🧠 HEALTH AI DASHBOARD REPORT", styles["Title"]))
    content.append(Spacer(1, 15))

    # 🔷 PATIENT DETAILS
    content.append(Paragraph("Patient Details", styles["Heading2"]))
    content.append(Paragraph(f"Name: {session.get('user')}", styles["Normal"]))
    content.append(Paragraph(f"Health Score: {session.get('score')}/100", styles["Normal"]))
    content.append(Spacer(1, 15))

    # 🔷 PARAMETERS TABLE
    data = session.get("data", {})

    table_data = [["Parameter", "Value", "Status"]]

    for k, v in data.items():

        status = "Normal"

        if k == "Hemoglobin" and v < 13:
            status = "Low"
        elif k == "Glucose" and v > 140:
            status = "High"
        elif k == "Cholesterol" and v > 200:
            status = "High"

        table_data.append([k, str(v), status])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))

    content.append(Paragraph("Blood Parameters", styles["Heading2"]))
    content.append(table)
    content.append(Spacer(1, 20))

    # 🔷 RISKS (BOX STYLE SIMULATION)
    content.append(Paragraph("Detected Risks", styles["Heading2"]))
    risks = session.get("risks", [])

    if risks:
        for r in risks:

            color = colors.green
            if r["severity"] == "High":
                color = colors.red
            elif r["severity"] == "Medium":
                color = colors.orange

            risk_table = Table([[f"{r['name']} - {r['severity']}"]])
            risk_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), color),
                ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
                ("BOX", (0,0), (-1,-1), 1, colors.black),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ]))

            content.append(risk_table)
            content.append(Spacer(1, 8))

    else:
        content.append(Paragraph("No risks detected", styles["Normal"]))

    content.append(Spacer(1, 15))

    # 🔷 EXPLANATION
    content.append(Paragraph("Explanation", styles["Heading2"]))
    for e in session.get("explanations", []):
        content.append(Paragraph(f"• {e}", styles["Normal"]))

    content.append(Spacer(1, 15))

    # 🔷 RECOMMENDATIONS
    content.append(Paragraph("Recommendations", styles["Heading2"]))
    for r in session.get("recommendations", []):
        content.append(Paragraph(f"• {r}", styles["Normal"]))

    doc.build(content)

    return send_file(file_path, as_attachment=True)
# ---------------- HISTORY ----------------
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT score,data FROM reports WHERE username=?", (session["user"],))
    reports = cur.fetchall()

    conn.close()

    return render_template("history.html", reports=reports)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)