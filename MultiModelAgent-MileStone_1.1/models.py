from config import REFERENCE_RANGES

class Model1_ParameterInterpretation:
    def analyze(self, data, context=None):
        results = {}
        gender = context.get('gender', 'male') if context else 'male'
        
        for param, value in data.items():
            if param not in REFERENCE_RANGES:
                continue
            
            ref = REFERENCE_RANGES[param]
            range_key = gender if gender in ref else 'normal'
            min_val, max_val = ref[range_key]
            
            if value < min_val:
                status = 'low'
            elif value > max_val:
                status = 'high'
            else:
                status = 'normal'
            
            results[param] = {
                'value': value,
                'status': status,
                'reference': f"{min_val}-{max_val} {ref['unit']}"
            }
        return results

class Model2_PatternRecognition:
    def analyze(self, data, context=None):
        risks = []
        
        if 'cholesterol_total' in data and data['cholesterol_total'] > 240:
            risks.append({'type': 'cardiovascular', 'level': 'high', 'reason': 'High total cholesterol'})
        
        if 'ldl' in data and 'hdl' in data:
            ratio = data['ldl'] / data['hdl'] if data['hdl'] > 0 else 0
            if ratio > 3.5:
                risks.append({'type': 'cardiovascular', 'level': 'elevated', 'reason': f'LDL/HDL ratio: {ratio:.2f}'})
        
        if 'glucose' in data and data['glucose'] > 125:
            risks.append({'type': 'diabetes', 'level': 'high', 'reason': 'Elevated fasting glucose'})
        
        if 'creatinine' in data and data['creatinine'] > 1.5:
            risks.append({'type': 'kidney', 'level': 'moderate', 'reason': 'Elevated creatinine'})
        
        return {'risks': risks, 'patterns': self._identify_patterns(data)}
    
    def _identify_patterns(self, data):
        patterns = []
        if data.get('glucose', 0) > 100 and data.get('triglycerides', 0) > 150:
            patterns.append('metabolic_syndrome_indicators')
        return patterns

class Model3_ContextualAnalysis:
    def analyze(self, interpretations, risks, context):
        if not context:
            return {}
        
        age = context.get('age', 0)
        adjustments = []
        
        if age > 60:
            adjustments.append('Age-related: Increased cardiovascular monitoring recommended')
        
        if context.get('family_history'):
            adjustments.append('Family history: Enhanced screening advised')
        
        return {'adjustments': adjustments, 'context_applied': True}
