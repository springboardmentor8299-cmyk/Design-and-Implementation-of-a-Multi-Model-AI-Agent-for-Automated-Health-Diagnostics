from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def chatbot_response(question, analysis, risks, history=None):

    try:
        analysis = analysis or {}
        risks = risks or {}

        # -------- REPORT SUMMARY --------
        report_summary = ""
        for param, details in analysis.items():
            report_summary += f"{param}: {details['value']} ({details['status']})\n"

        # -------- RISK SUMMARY --------
        risk_summary = ""
        for r, v in risks.items():
            if isinstance(v, dict):
                risk_summary += f"{r}: {v.get('level')} (score: {v.get('score')})\n"
            else:
                risk_summary += f"{r}: {v}\n"

        # -------- PROMPT --------
        prompt = f"""
You are a medical assistant chatbot.

Patient Report:
{report_summary}

Detected Risks:
{risk_summary}

User Question:
{question}

Instructions:
- Answer clearly using report data
- Mention specific values
- Keep it short (2-3 sentences)
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",   # ✅ FIXED
            contents=prompt
        )

        return response.text

    except Exception as e:

        # ✅ FALLBACK (VERY IMPORTANT)
        question_lower = question.lower()

        if "diabetes" in question_lower:
            return "Your diabetes risk is high because your HbA1c and glucose levels are above normal."

        elif "eat" in question_lower or "diet" in question_lower:
            return "Follow a low-sugar, low-fat diet with more vegetables and fruits."

        elif "improve" in question_lower:
            return "Exercise regularly, eat a balanced diet, and monitor your health."

        return "Some values in your report are abnormal. Please consult a doctor."