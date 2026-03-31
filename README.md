# Multi-Model AI Agent for Automated Health Diagnostics

An AI-powered system for analyzing blood test reports and providing automated health diagnostics.

## Features

- **PDF/Image Upload**: Supports PDF and image formats (PNG, JPG, JPEG)
- **OCR Processing**: Extracts text from scanned documents using Tesseract
- **Parameter Extraction**: Identifies and extracts blood test parameters
- **AI Analysis**: Uses Google Gemini AI for intelligent data extraction
- **Comparative Analysis**: Compares results against standard medical ranges
- **Web Interface**: Two interfaces available (Flask and Streamlit)

## Project Structure

```
├── Agent.py                 # Streamlit app with Gemini AI integration
├── app.py                   # Flask web application
├── extractor.py             # Text extraction and parameter parsing
├── model1.py                # Parameter interpretation module
├── src/
│   ├── data_extraction.py   # Data extraction engine
│   └── data_validation.py   # Data validation module
├── templates/
│   └── index.html           # Flask HTML template
└── requirements.txt         # Python dependencies
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Update the path in `extractor.py` and `app.py` if needed

3. Set up environment variables:
```bash
copy .env.example .env
# Edit .env and add your Gemini API key
```

## Usage

### Option 1: Flask Web App
```bash

cd "Design-and-Implementation-of-a-Multi-Model-AI-Agent-for-Automated-Health-Diagnostics"
python -m streamlit run Agent.py

Visit http://localhost:5000

### Option 2: Streamlit App (with AI)
```bash
streamlit run Agent.py
```

### Option 3: Basic Streamlit App
```bash
cd Design-and-Implementation-of-a-Multi-Model-AI-Agent-for-Automated-Health-Diagnostics
streamlit run app.py
```

## Supported Blood Parameters

- Hemoglobin
- WBC Count
- Platelet Count
- Glucose (Fasting/Post-Prandial)
- HbA1c
- Cholesterol (Total, HDL, LDL)
- Triglycerides
- Liver Function (SGOT, SGPT, ALP, Bilirubin)
- Kidney Function (Urea, Creatinine)
- Thyroid (TSH, T3, T4)

## Notes

- This tool is for informational purposes only
- Always consult a healthcare professional for medical advice
- Ensure Tesseract OCR is properly installed for image processing
