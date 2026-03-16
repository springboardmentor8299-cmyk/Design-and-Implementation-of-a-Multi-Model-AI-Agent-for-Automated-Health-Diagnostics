import os
from dotenv import load_dotenv

load_dotenv()

PRIVATE_API_URL = os.getenv('PRIVATE_API_URL', 'http://localhost:11434/api/generate')
PRIVATE_API_KEY = os.getenv('PRIVATE_API_KEY', '')
MODEL_NAME = os.getenv('MODEL_NAME', 'llama2')
REFERENCE_RANGES = {
    'hemoglobin': {'male': (13.5, 17.5), 'female': (12.0, 15.5), 'unit': 'g/dL'},
    'glucose': {'normal': (70, 100), 'unit': 'mg/dL'},
    'cholesterol_total': {'normal': (0, 200), 'unit': 'mg/dL'},
    'ldl': {'normal': (0, 100), 'unit': 'mg/dL'},
    'hdl': {'male': (40, 999), 'female': (50, 999), 'unit': 'mg/dL'},
    'triglycerides': {'normal': (0, 150), 'unit': 'mg/dL'},
    'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1), 'unit': 'mg/dL'},
    'wbc': {'normal': (4.5, 11.0), 'unit': '10^3/μL'},
    'platelets': {'normal': (150, 400), 'unit': '10^3/μL'}
}
