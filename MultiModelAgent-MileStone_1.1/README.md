# Multi-Model AI Agent for Automated Health Diagnostics

An intelligent system for automated interpretation of blood reports with personalized health recommendations.

## Features

- **Multi-format Input**: Supports PDF, images (PNG/JPG), and JSON
- **Three-Model Analysis**:
  - Model 1: Parameter interpretation against reference ranges
  - Model 2: Pattern recognition and risk assessment
  - Model 3: Contextual analysis with user demographics
- **Personalized Recommendations**: AI-generated health advice
- **Streamlit UI**: Interactive web interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
copy .env.example .env
# Edit .env and add your OpenAI API key (optional - system works without it using rule-based recommendations)
```

3. Install Tesseract OCR (for image processing):
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Browser will open automatically to the Streamlit interface

3. Upload blood report, provide context (age, gender, family history), and click Analyze

## Testing

Use the provided sample:
- Upload `sample_report.json` through the interface
- Or view sample data in the sidebar

## Architecture

- **Data Extractor**: Handles PDF/Image/JSON parsing
- **Data Validator**: Cleans and standardizes data
- **Model 1**: Parameter interpretation
- **Model 2**: Pattern recognition & risk assessment
- **Model 3**: Contextual analysis
- **Synthesis Engine**: Aggregates findings
- **Recommendation Generator**: Creates personalized advice
- **Orchestrator**: Manages workflow

## Disclaimer

This system provides AI-based interpretations and is NOT a substitute for professional medical advice. Always consult healthcare providers for medical decisions.
