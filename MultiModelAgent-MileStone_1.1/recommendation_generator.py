import requests
from config import PRIVATE_API_URL, PRIVATE_API_KEY, MODEL_NAME

class RecommendationGenerator:
    def __init__(self):
        self.api_url = PRIVATE_API_URL
        self.api_key = PRIVATE_API_KEY
        self.model = MODEL_NAME
    
    def generate(self, findings):
        try:
            prompt = f"""Based on these blood test findings, provide personalized health recommendations:
{findings['summary']}

Abnormal parameters: {findings['interpretations']}
Risks: {findings['risks']}

Provide 3-5 actionable recommendations covering diet, lifestyle, and follow-up actions."""
            
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('response', self._generate_rule_based(findings))
            else:
                return self._generate_rule_based(findings)
        except:
            return self._generate_rule_based(findings)
    
    def _generate_rule_based(self, findings):
        recommendations = []
        
        for param, data in findings['interpretations'].items():
            if data['status'] == 'high':
                if param == 'glucose':
                    recommendations.append("Reduce sugar intake and increase physical activity")
                elif param in ['cholesterol_total', 'ldl']:
                    recommendations.append("Adopt a heart-healthy diet low in saturated fats")
                elif param == 'creatinine':
                    recommendations.append("Stay hydrated and consult a nephrologist")
        
        if findings['risks'].get('risks'):
            recommendations.append("Schedule a follow-up with your healthcare provider")
        
        return '\n'.join(recommendations) if recommendations else "Maintain current healthy lifestyle"
