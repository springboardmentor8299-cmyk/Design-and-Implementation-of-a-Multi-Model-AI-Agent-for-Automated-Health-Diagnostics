# backend/chatbot.py
"""
AI Chatbot Module
Answers user health queries using:
  1. Groq LLM API (if API key is configured)
  2. Rule-based fallback responses
"""

import os
import re
import logging

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Rule-based responses for common health questions
RULE_BASED_RESPONSES = {
    "cholesterol": (
        "🫀 Cholesterol Basics:\n"
        "• Total Cholesterol: Aim for < 200 mg/dL (desirable)\n"
        "• LDL (bad cholesterol): Aim for < 100 mg/dL (optimal)\n"
        "• HDL (good cholesterol): Higher is better; > 60 mg/dL is protective\n"
        "• Triglycerides: Aim for < 150 mg/dL\n\n"
        "To lower cholesterol: reduce saturated/trans fats, increase fiber, "
        "exercise regularly, and consider medication if levels remain high."
    ),
    "diabetes": (
        "🍬 Diabetes Key Facts:\n"
        "• Fasting glucose ≥ 126 mg/dL = Diabetes\n"
        "• Fasting glucose 100–125 mg/dL = Pre-diabetes\n"
        "• HbA1c ≥ 6.5% = Diabetes; 5.7–6.4% = Pre-diabetes\n\n"
        "Management: Low-GI diet, regular exercise, blood sugar monitoring, "
        "and medications as prescribed. Early intervention can reverse pre-diabetes."
    ),
    "hemoglobin": (
        "🩸 Hemoglobin Reference Ranges:\n"
        "• Men: 13.5–17.5 g/dL\n"
        "• Women: 12.0–15.5 g/dL\n\n"
        "Low hemoglobin suggests anemia. Common causes: iron deficiency, "
        "B12/folate deficiency, chronic disease, or blood loss. "
        "High hemoglobin may indicate dehydration or polycythemia."
    ),
    "blood pressure": (
        "💉 Blood Pressure Categories:\n"
        "• Normal: < 120/80 mmHg\n"
        "• Elevated: 120–129 / < 80 mmHg\n"
        "• High (Stage 1): 130–139 / 80–89 mmHg\n"
        "• High (Stage 2): ≥ 140 / ≥ 90 mmHg\n\n"
        "Note: Blood pressure is not measured in a blood test but is a key cardiovascular risk factor."
    ),
    "creatinine": (
        "🫘 Creatinine & Kidney Function:\n"
        "• Normal creatinine: Men 0.74–1.35 mg/dL, Women 0.59–1.04 mg/dL\n"
        "• Elevated creatinine may indicate kidney stress or disease\n"
        "• eGFR > 60 mL/min/1.73m² is generally normal\n\n"
        "Stay well-hydrated and avoid NSAIDs/nephrotoxic medications if kidneys are stressed."
    ),
    "vitamin d": (
        "☀️ Vitamin D Status:\n"
        "• Deficient: < 20 ng/mL\n"
        "• Insufficient: 20–29 ng/mL\n"
        "• Sufficient: 30–100 ng/mL\n\n"
        "Sources: sunlight (15–20 min/day), fatty fish, eggs, fortified foods. "
        "Supplements (1000–2000 IU/day) often needed, especially in India/South Asia."
    ),
    "thyroid": (
        "🦋 Thyroid Function:\n"
        "• Normal TSH: 0.4–4.0 mIU/L\n"
        "• TSH > 4.0: Suggests hypothyroidism (underactive thyroid)\n"
        "• TSH < 0.4: Suggests hyperthyroidism (overactive thyroid)\n\n"
        "Hypothyroidism symptoms: fatigue, weight gain, cold intolerance. "
        "Always confirm with Free T3/T4 and physician evaluation."
    ),
    "triglycerides": (
        "📊 Triglycerides:\n"
        "• Normal: < 150 mg/dL\n"
        "• Borderline: 150–199 mg/dL\n"
        "• High: 200–499 mg/dL\n"
        "• Very High: ≥ 500 mg/dL (pancreatitis risk)\n\n"
        "To lower: reduce sugar/refined carbs, alcohol, increase omega-3 fatty acids and exercise."
    ),
    "liver": (
        "🫁 Liver Function Tests:\n"
        "• ALT: 7–56 U/L (men), 7–45 U/L (women)\n"
        "• AST: 10–40 U/L\n"
        "• Bilirubin: 0.1–1.2 mg/dL\n"
        "• ALP: 44–147 U/L\n\n"
        "Elevated liver enzymes may indicate fatty liver, hepatitis, or medication effects. "
        "Avoid alcohol and hepatotoxic drugs."
    ),
    "wbc": (
        "🦠 White Blood Cells (WBC):\n"
        "• Normal: 4.5–11.0 thousand/µL\n"
        "• High WBC: May indicate infection, inflammation, or rarely leukemia\n"
        "• Low WBC: May indicate viral infection, bone marrow issues, or immunosuppression\n\n"
        "A differential WBC count helps identify the specific type of immune response."
    ),
    "hba1c": (
        "📊 HbA1c (Glycated Hemoglobin):\n"
        "• Normal: < 5.7%\n"
        "• Pre-diabetes: 5.7–6.4%\n"
        "• Diabetes: ≥ 6.5%\n\n"
        "HbA1c reflects average blood sugar over the past 2–3 months. "
        "Target for people with diabetes is typically < 7% (as advised by your doctor)."
    ),
    "health score": (
        "💯 About Your Health Score:\n\n"
        "The Health Score (0–100) is a composite indicator based on how many blood "
        "parameters fall within normal ranges:\n"
        "• 85–100: Excellent health markers\n"
        "• 70–84: Good overall markers\n"
        "• 55–69: Fair — some parameters need attention\n"
        "• 40–54: Below average — medical consultation advised\n"
        "• < 40: Poor — urgent medical evaluation needed\n\n"
        "This score is indicative and NOT a substitute for clinical diagnosis."
    ),
}

FALLBACK_RESPONSE = (
    "I'm sorry, I don't have a specific answer for that question in my knowledge base. "
    "For detailed medical advice, please consult a qualified healthcare professional. "
    "You can also ask me about specific blood parameters, health conditions, or what your "
    "test results mean!"
)


class Chatbot:

    def __init__(self, analysis_context: dict = None):
        """
        analysis_context: the full analysis result dict so the chatbot can
        answer questions specifically about the user's report.
        """
        self.context = analysis_context or {}
        self.groq_available = bool(GROQ_API_KEY)

    def chat(self, user_message: str, chat_history: list = None) -> str:
        """
        Main entry point. Tries Groq first, falls back to rule-based.
        Returns the bot response string.
        """
        if self.groq_available:
            try:
                return self._groq_chat(user_message, chat_history or [])
            except Exception as e:
                logger.warning(f"Groq API failed: {e}. Falling back to rule-based.")

        return self._rule_based_chat(user_message)

    # ── Groq LLM Chat ─────────────────────────────────────────────────────────

    def _groq_chat(self, user_message: str, chat_history: list) -> str:
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq package not installed")

        client = Groq(api_key=GROQ_API_KEY)

        system_prompt = self._build_system_prompt()

        messages = [{"role": "system", "content": system_prompt}]
        # Add history (last 6 turns)
        for turn in chat_history[-6:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model      = "llama3-8b-8192",
            messages   = messages,
            max_tokens = 600,
            temperature= 0.4,
        )
        return response.choices[0].message.content.strip()

    def _build_system_prompt(self) -> str:
        ctx_summary = ""
        if self.context:
            health_score = self.context.get("scores", {}).get("health_score", {})
            patterns     = [p["name"] for p in self.context.get("patterns", [])]
            abnormal     = [c["display_name"] for c in self.context.get("classified", [])
                            if c["status"] != "Normal"]

            ctx_summary = (
                f"\n\nCurrent patient's analysis context:\n"
                f"- Health Score: {health_score.get('score','N/A')}/100 ({health_score.get('label','N/A')})\n"
                f"- Detected Patterns: {', '.join(patterns) if patterns else 'None'}\n"
                f"- Abnormal Parameters: {', '.join(abnormal) if abnormal else 'None'}\n"
            )

        return (
            "You are Healytics, a helpful and empathetic AI health assistant embedded in a "
            "blood report analysis application. Your role is to:\n"
            "1. Explain blood test parameters and what abnormal values mean\n"
            "2. Provide general health and lifestyle advice based on findings\n"
            "3. Answer questions about nutrition, exercise, and preventive health\n"
            "4. ALWAYS recommend consulting a qualified healthcare professional for diagnosis/treatment\n"
            "5. Keep responses clear, concise, and non-alarmist\n"
            "6. Never diagnose or prescribe — provide education and guidance only\n"
            f"{ctx_summary}\n"
            "Format responses with clear structure. Use bullet points where appropriate. "
            "Be warm, supportive, and medically accurate."
        )

    # ── Rule-Based Fallback ───────────────────────────────────────────────────

    def _rule_based_chat(self, user_message: str) -> str:
        msg_lower = user_message.lower()

        # Check for greeting
        if any(w in msg_lower for w in ["hello", "hi", "hey", "greet"]):
            return (
                "👋 Hello! I'm Healytics, your health report assistant.\n\n"
                "I can help you understand your blood test results, explain what different "
                "parameters mean, and provide general health guidance. What would you like to know?"
            )

        # Check for report-specific questions
        if any(w in msg_lower for w in ["my report", "my result", "my score", "what does my"]):
            return self._answer_about_report()

        # Keyword matching for health topics
        for keyword, response in RULE_BASED_RESPONSES.items():
            if keyword in msg_lower:
                return response

        # Check for specific parameter names
        if "glucose" in msg_lower or "blood sugar" in msg_lower:
            return RULE_BASED_RESPONSES["diabetes"]
        if "hdl" in msg_lower or "ldl" in msg_lower or "lipid" in msg_lower:
            return RULE_BASED_RESPONSES["cholesterol"]
        if "alt" in msg_lower or "ast" in msg_lower or "bilirubin" in msg_lower:
            return RULE_BASED_RESPONSES["liver"]
        if "b12" in msg_lower or "vitamin b" in msg_lower:
            return RULE_BASED_RESPONSES["vitamin d"].replace("Vitamin D", "Vitamin B12")
        if "platelet" in msg_lower:
            return (
                "🩺 Platelets:\n"
                "• Normal: 150,000–400,000 per µL\n"
                "• Low platelets (thrombocytopenia): increased bleeding risk\n"
                "• High platelets (thrombocytosis): possible clotting risk\n\n"
                "Platelets are essential for blood clotting. Abnormal values need medical evaluation."
            )
        if any(w in msg_lower for w in ["diet", "food", "eat", "nutrition"]):
            return (
                "🥗 General Dietary Recommendations:\n"
                "• Eat plenty of fruits and vegetables (5+ servings/day)\n"
                "• Choose whole grains over refined carbohydrates\n"
                "• Include lean protein: fish, poultry, legumes\n"
                "• Use healthy fats: olive oil, avocado, nuts\n"
                "• Limit: red meat, processed foods, added sugar, alcohol\n"
                "• Stay hydrated: 8–10 glasses of water per day\n\n"
                "For personalized dietary advice based on your blood results, consult a registered dietitian."
            )
        if any(w in msg_lower for w in ["exercise", "workout", "physical", "fitness"]):
            return (
                "🏃 Exercise Recommendations:\n"
                "• Aim for 150 min/week of moderate aerobic activity (brisk walking, cycling)\n"
                "• Include strength training 2–3 times per week\n"
                "• Even 30 minutes of daily walking significantly improves metabolic health\n"
                "• Exercise improves blood sugar, cholesterol, blood pressure, and mental health\n\n"
                "Start gradually and increase intensity over time. Consult your doctor before "
                "starting a new exercise program if you have existing health conditions."
            )
        if any(w in msg_lower for w in ["disclaimer", "accurate", "trust", "reliable"]):
            return (
                "ℹ️ Important Disclaimer:\n\n"
                "Healytics provides educational information and AI-generated insights "
                "based on your blood report data. This is NOT a substitute for professional "
                "medical advice, diagnosis, or treatment.\n\n"
                "Always consult a qualified healthcare professional (doctor, specialist) for:\n"
                "• Interpreting your test results in full clinical context\n"
                "• Diagnosis of any medical condition\n"
                "• Treatment decisions and medication\n\n"
                "AI analysis has limitations and may not account for all individual factors."
            )

        return FALLBACK_RESPONSE

    def _answer_about_report(self) -> str:
        if not self.context:
            return (
                "I don't have a report analyzed yet. Please upload and analyze a blood report "
                "first, then I can answer specific questions about your results!"
            )

        health_score = self.context.get("scores", {}).get("health_score", {})
        patterns     = self.context.get("patterns", [])
        abnormal     = [c for c in self.context.get("classified", []) if c["status"] != "Normal"]
        score        = health_score.get("score", "N/A")
        label        = health_score.get("label", "N/A")

        response = f"📋 Summary of Your Blood Report Analysis:\n\n"
        response += f"🎯 Health Score: {score}/100 ({label})\n\n"

        if abnormal:
            response += f"⚠️ {len(abnormal)} parameter(s) outside normal range:\n"
            for a in abnormal[:5]:
                response += f"  • {a['display_name']}: {a['value']} {a['unit']} ({a['status']})\n"
            if len(abnormal) > 5:
                response += f"  ... and {len(abnormal)-5} more\n"
            response += "\n"

        if patterns:
            response += f"🔍 {len(patterns)} clinical pattern(s) detected:\n"
            for p in patterns[:3]:
                response += f"  • {p['icon']} {p['name']}\n"
            response += "\n"

        response += "Ask me about any specific parameter or pattern for more details!"
        return response