# Quick Start Guide

## Run the Application

### Option 1: Direct Run (Recommended)
```bash
cd MultiModelAgent-MileStone_1.1
streamlit run app.py
```

### Option 2: With Virtual Environment
```bash
cd MultiModelAgent-MileStone_1.1
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

### Test Pattern Recognition & Risk Assessment
```bash
cd MultiModelAgent-MileStone_1.1
python test_model2_model3.py
```

### Test Risk Plausibility
```bash
cd MultiModelAgent-MileStone_1.1
python generate_synthetic_data.py
python evaluate_risk_plausibility.py
```

## Using the Application

1. Open browser (automatically opens at http://localhost:8501)
2. Upload blood report (PDF, Image, or JSON)
3. Enter patient context:
   - Age
   - Gender
   - Family History (optional)
4. Click "Analyze Report"
5. View results:
   - Parameter interpretations
   - Patterns identified
   - Risk scores
   - Contextual adjustments
   - Recommendations

## Sample JSON Input
Create a file `sample_report.json`:
```json
{
  "hemoglobin": 14.5,
  "glucose": 110,
  "cholesterol_total": 250,
  "ldl": 160,
  "hdl": 35,
  "triglycerides": 180,
  "creatinine": 1.0
}
```

Upload this file to test the system.

## Troubleshooting

**If streamlit not found:**
```bash
pip install streamlit
```

**If other packages missing:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```
