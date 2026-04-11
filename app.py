from flask import Flask, render_template, request
import os
import json
from datetime import datetime
from extractor import run_extraction
from model1 import interpret_parameters
from model2 import detect_health_patterns
from synthesis import synthesize_findings
from recommendations import generate_recommendations
from severity import get_severity   # ⭐ NEW
from flask import send_file
from fpdf import FPDF
from gemini_chatbot import chatbot_response
import pytesseract



pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
# ⭐ GLOBAL STORAGE
last_report = {}
chat_history_global = []

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def home():

    extracted = None
    analysis = None
    risks = None
    summary = None
    recommendations = None
    severity = None
    health_stats = None
    health_status = None 
    chat_response = None
    global chat_history_global
    chat_history = chat_history_global

    if request.method == "POST":

        # ---------- FILE UPLOAD ----------
        if "file" in request.files:

            file = request.files["file"]

            if file.filename == "":
                return "No file selected"

            if file:
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)

                extracted = run_extraction(path, "WEB001")

                # ⭐ ADD THIS BLOCK HERE
                age = request.form.get("age")
                gender = request.form.get("gender")

                if age:
                    try:
                        extracted["age"] = float(age)
                    except:
                        pass

                if gender:
                    extracted["gender"] = gender
                from orchestrator import run_pipeline

                pipeline_output = run_pipeline(extracted)

                analysis = pipeline_output["analysis"]
                risks = pipeline_output["risks"]
                severity = pipeline_output["severity"]
                summary = pipeline_output["summary"]
                recommendations = pipeline_output["recommendations"]

                report_data = {
                        "date": str(datetime.now()),
                        "analysis": analysis,
                        "risks": risks,
                        "severity": severity,
                        "summary": summary,
                        "recommendations": recommendations,
                        "patient_name": extracted.get("patient_name"),
                        "age": extracted.get("age"),
                        "gender": extracted.get("gender")
                }

                global last_report
                last_report = report_data

                with open("reports.json", "a") as f:
                    f.write(json.dumps(report_data, default=str) + "\n")

        # ---------- CHATBOT ----------
        elif "chat" in request.form:

            user_question = request.form.get("question")

            if user_question and last_report:

                bot_reply = chatbot_response(
                    user_question,
                    last_report.get("analysis"),   # ✅ FIX
                    last_report.get("risks"),
                    chat_history
                )

                chat_history_global.append(("You", user_question))
                if bot_reply:
                    chat_history_global.append(("Bot", bot_reply))

    # ---------- HEALTH STATS ----------
    if analysis:
        total = len(analysis)

        normal_count = sum(1 for v in analysis.values() if v.get("status") == "NORMAL")
        high_count = sum(1 for v in analysis.values() if v.get("status") == "HIGH")
        low_count = sum(1 for v in analysis.values() if v.get("status") == "LOW")

        health_score = round((normal_count / total * 100) if total else 0)

        if health_score >= 75:
            health_status = "Good"
        elif health_score >= 40:
            health_status = "Moderate"
        else:
            health_status = "Poor"

        health_stats = {
            "total": total,
            "normal": normal_count,
            "high": high_count,
            "low": low_count,
            "score": min(100, health_score),
            "status": health_status
        }

    return render_template(
        "index.html",
        extracted=extracted,
        analysis=analysis,
        risks=risks,
        show_download = True,
        severity=severity,
        summary=summary,
        recommendations=recommendations,
        health_stats=health_stats,
        health_status=health_status,
        chat_history=chat_history_global
    )


def section_title(pdf, title):
    pdf.set_fill_color(200, 230, 226)
    pdf.set_text_color(13, 92, 82)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"  {title}", ln=True, fill=True)
    pdf.ln(2)

@app.route("/download")

def download_report():

    if not last_report:
        return "No report available. Please upload a file first."

    pdf = FPDF()
    pdf.add_page()

    # ---------- HEADER ----------
    pdf.set_fill_color(13, 92, 82)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 14, "  AI HEALTH ANALYSIS REPORT", ln=True, fill=True)

    pdf.ln(4)

    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, "Generated by Health AI System", ln=True)

    pdf.ln(5)

    # Reset color
    pdf.set_text_color(0, 0, 0)

    # ---------- DATE ----------
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Date: {last_report.get('date')}", ln=True)

    pdf.ln(2)

    # -------- PATIENT INFO --------
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Patient Information", ln=True)

    pdf.set_font("Arial", size=10)

    name = last_report.get("patient_name", "N/A")
    age = last_report.get("age", "N/A")
    gender = last_report.get("gender", "N/A")

    pdf.cell(0, 6, f"Name: {name}", ln=True)
    pdf.cell(0, 6, f"Age: {age}", ln=True)
    pdf.cell(0, 6, f"Gender: {gender}", ln=True)

    pdf.ln(4)

    pdf.ln(3)

    # -------- HEALTH SCORE --------
    score = 0
    if last_report.get("analysis"):
        total = len(last_report["analysis"])
        normal = sum(1 for v in last_report["analysis"].values() if v["status"] == "NORMAL")
        score = int((normal / total) * 100) if total else 0

    section_title(pdf, "Overall Health Score")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Score: {score}%", ln=True)

    # Draw bar
    bar_width = 100
    filled = int((score / 100) * bar_width)

    pdf.set_fill_color(20, 184, 166)  # green
    pdf.cell(filled, 8, "", fill=True)

    pdf.set_fill_color(220, 220, 220)  # gray
    pdf.cell(bar_width - filled, 8, "", fill=True, ln=True)

    pdf.ln(5)

    # -------- PARAMETER OVERVIEW --------
    section_title(pdf, "Parameter Overview")

    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 8, "Parameter", border=1)
    pdf.cell(40, 8, "Value", border=1)
    pdf.cell(40, 8, "Status", border=1, ln=True)

    pdf.set_font("Arial", size=10)

    analysis = last_report.get("analysis", {})

    for param, info in analysis.items():

        status = info["status"]

        if status == "HIGH":
            pdf.set_text_color(220, 38, 38)
        elif status == "LOW":
            pdf.set_text_color(217, 119, 6)
        else:
            pdf.set_text_color(20, 184, 166)

        pdf.cell(80, 8, param, border=1)
        pdf.cell(40, 8, str(info["value"]), border=1)
        pdf.cell(40, 8, status, border=1, ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # ---------- SEVERITY TABLE ----------
    section_title(pdf, "Risk Severity Overview")

    pdf.set_font("Arial", "B", 10)

    # Table header
    pdf.set_fill_color(200, 230, 226)
    pdf.cell(100, 8, "Condition", border=1, fill=True)
    pdf.cell(40, 8, "Severity", border=1, fill=True, ln=True)

    pdf.set_font("Arial", size=10)

    severity = last_report.get("severity", {})

    for condition, level in severity.items():

        if level == "HIGH":
            pdf.set_text_color(220, 38, 38)
        elif level == "MEDIUM":
            pdf.set_text_color(217, 119, 6)
        else:
            pdf.set_text_color(20, 184, 166)

        pdf.cell(100, 8, condition, border=1)
        pdf.cell(40, 8, level, border=1, ln=True)

    pdf.set_text_color(0, 0, 0)

    pdf.ln(5)

    # -------- KEY HEALTH RISKS --------
    section_title(pdf, "Key Health Risks")

    risks = last_report.get("risks", {})

    for risk, info in risks.items():
        pdf.set_fill_color(255, 240, 240)
        pdf.multi_cell(
            0,
            8,
            f"{risk}: {info.get('level')} (Score: {info.get('score')})",
            fill=True
        )
        pdf.ln(1)

    pdf.ln(3)

    # ---------- SUMMARY ----------
    section_title(pdf, "Summary")

    pdf.set_font("Arial", size=10)

    summary = last_report.get("summary", [])

    if isinstance(summary, list):
        for item in summary:
            pdf.multi_cell(0, 6, f"- {item}")
            pdf.ln(1)
    else:
        pdf.multi_cell(0, 6, str(summary))

    pdf.ln(4)

    # ---------- RECOMMENDATIONS ----------
    section_title(pdf, "Recommendations")

    pdf.set_font("Arial", size=10)

    recs = last_report.get("recommendations", [])

    for rec in recs:
        pdf.multi_cell(0, 6, f"- {rec}")
        pdf.ln(1)

    pdf.ln(4)

    # ---------- FOOTER LINE ----------
    pdf.set_draw_color(13, 92, 82)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.ln(3)

    # ---------- DISCLAIMER ----------
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0,
        5,
        "Disclaimer: This AI-generated report is for informational purposes only and should not replace professional medical advice."
    )

    # ---------- SAVE ----------
    file_path = "report.pdf"
    pdf.output(file_path)

    return send_file(file_path, as_attachment=True)

@app.route("/download")
def download():
    return send_file("report.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)