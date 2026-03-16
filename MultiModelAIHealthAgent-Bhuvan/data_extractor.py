import json
import re
from PyPDF2 import PdfReader
from PIL import Image


class DataExtractor:
    def extract(self, file_path, file_type):
        if file_type == 'pdf':
            return self._extract_pdf(file_path)
        
        return {}
    
    
    
    def _extract_pdf(self, file_path):
        reader = PdfReader(file_path)
        text = ''.join(page.extract_text() for page in reader.pages)
        return self._parse_text(text)
    
   
    
    def _parse_text(self, text):
        data = {}
        patterns = {
            'hemoglobin': r'hemoglobin[:\s]+(\d+\.?\d*)',
            'glucose': r'glucose[:\s]+(\d+\.?\d*)',
            'cholesterol': r'cholesterol[:\s]+(\d+\.?\d*)',
            'ldl': r'ldl[:\s]+(\d+\.?\d*)',
            'hdl': r'hdl[:\s]+(\d+\.?\d*)',
            'triglycerides': r'triglycerides[:\s]+(\d+\.?\d*)',
            'creatinine': r'creatinine[:\s]+(\d+\.?\d*)',
            'wbc': r'wbc[:\s]+(\d+\.?\d*)',
            'platelets': r'platelets[:\s]+(\d+\.?\d*)'
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                data[key] = float(match.group(1))
        return data
