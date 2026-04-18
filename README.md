# 🩺 Multi-Model AI Agent for Automated Health Diagnostics

## 📌 Project Overview

This project is a **Multimodal AI-based Health Diagnostic System** that analyzes medical reports (such as blood test reports) and provides intelligent insights about a patient’s health condition.

The system integrates multiple modules including:

* Data extraction from reports
* Health pattern detection
* Risk analysis
* Severity estimation
* AI-powered chatbot for explanations

---

## 🚀 Features

* 📄 Extracts data from medical reports (PDF/Text)
* 🧠 Detects health conditions using multiple models
* ⚠️ Risk analysis and severity prediction
* 💡 Generates personalized recommendations
* 🤖 Gemini-powered chatbot for user queries
* 🌐 Web interface using Flask

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **AI Integration:** Google Gemini API
* **Data Processing:** NumPy, Pandas
* **PDF Processing:** PyPDF2 / pdfplumber
* **Environment Management:** python-dotenv

---

## 📁 Project Structure

```
health-ai-project/
│── app.py
│── gemini_chatbot.py
│── extractor.py
│── model1.py / model2.py / model3.py
│── pipeline.py
│── templates/
│    └── index.html
│── requirements.txt
│── .gitignore
│── reports.json
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-repo-link.git
cd health-ai-project
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Add API Key (IMPORTANT 🔐)

Create a `.env` file in the root directory:

```
GEMINI_API_KEY=your_api_key_here
```

⚠️ Note: `.env` is not uploaded to GitHub for security reasons.

---

### 5️⃣ Run the Application

```bash
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

## 🤖 How It Works

1. User uploads or inputs medical report data
2. System extracts parameters from the report
3. Multiple models analyze patterns
4. Risk and severity are calculated
5. Recommendations are generated
6. Chatbot explains results interactively

---

## 🔒 Security

* API keys are stored securely using `.env`
* Sensitive files are excluded using `.gitignore`

---

## 📌 Future Enhancements

* Integration with real hospital APIs
* Advanced ML models for prediction
* User authentication system
* Mobile application support

---

## 👩‍💻 Author

**Varsha S Panicker**
B.Tech Computer Science Engineering

---

## 📄 License

This project is for educational and research purposes.
