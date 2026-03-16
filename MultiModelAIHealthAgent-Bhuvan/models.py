from config import REFERENCE_RANGES
import math

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
        patterns = self._identify_patterns(data, context)
        risks = self._calculate_risk_scores(data, context)
        correlations = self._identify_correlations(data)
        
        return {
            'patterns': patterns,
            'risks': risks,
            'correlations': correlations
        }
    
    def _identify_patterns(self, data, context):
        patterns = []
        
        # Metabolic Syndrome Pattern
        metabolic_indicators = 0
        if data.get('triglycerides', 0) >= 150: metabolic_indicators += 1
        if data.get('hdl', 999) < 40: metabolic_indicators += 1
        if data.get('glucose', 0) >= 100: metabolic_indicators += 1
        if metabolic_indicators >= 2:
            patterns.append({
                'name': 'metabolic_syndrome',
                'confidence': metabolic_indicators / 3,
                'indicators': metabolic_indicators
            })
        
        # Dyslipidemia Pattern
        if data.get('cholesterol_total', 0) > 240 or data.get('ldl', 0) > 160 or data.get('triglycerides', 0) > 200:
            patterns.append({
                'name': 'dyslipidemia',
                'confidence': 0.9,
                'indicators': 'abnormal_lipid_profile'
            })
        
        # Prediabetes/Diabetes Pattern
        glucose = data.get('glucose', 0)
        if 100 <= glucose < 126:
            patterns.append({'name': 'prediabetes', 'confidence': 0.85, 'glucose': glucose})
        elif glucose >= 126:
            patterns.append({'name': 'diabetes_indicator', 'confidence': 0.95, 'glucose': glucose})
        
        # Kidney Function Pattern
        if data.get('creatinine', 0) > 1.5:
            patterns.append({'name': 'kidney_dysfunction', 'confidence': 0.8, 'creatinine': data['creatinine']})
        
        # Anemia Pattern
        hb = data.get('hemoglobin', 999)
        gender = context.get('gender', 'male') if context else 'male'
        if (gender == 'male' and hb < 13.5) or (gender == 'female' and hb < 12.0):
            patterns.append({'name': 'anemia', 'confidence': 0.9, 'hemoglobin': hb})
        
        return patterns
    
    def _calculate_risk_scores(self, data, context):
        risks = []
        
        # Cardiovascular Risk Score (Framingham-inspired)
        cv_risk = self._calculate_cv_risk(data, context)
        if cv_risk:
            risks.append(cv_risk)
        
        # Diabetes Risk Score
        diabetes_risk = self._calculate_diabetes_risk(data, context)
        if diabetes_risk:
            risks.append(diabetes_risk)
        
        # Kidney Disease Risk
        kidney_risk = self._calculate_kidney_risk(data)
        if kidney_risk:
            risks.append(kidney_risk)
        
        return risks
    
    def _calculate_cv_risk(self, data, context):
        score = 0
        factors = []
        
        # Lipid ratios
        if 'cholesterol_total' in data and 'hdl' in data and data['hdl'] > 0:
            tc_hdl_ratio = data['cholesterol_total'] / data['hdl']
            if tc_hdl_ratio > 5:
                score += 3
                factors.append(f'TC/HDL ratio: {tc_hdl_ratio:.2f}')
            elif tc_hdl_ratio > 4:
                score += 2
                factors.append(f'TC/HDL ratio: {tc_hdl_ratio:.2f}')
        
        if 'ldl' in data and 'hdl' in data and data['hdl'] > 0:
            ldl_hdl_ratio = data['ldl'] / data['hdl']
            if ldl_hdl_ratio > 3.5:
                score += 2
                factors.append(f'LDL/HDL ratio: {ldl_hdl_ratio:.2f}')
        
        # Individual parameters
        if data.get('cholesterol_total', 0) > 240:
            score += 2
            factors.append('High total cholesterol')
        if data.get('ldl', 0) > 160:
            score += 2
            factors.append('High LDL')
        if data.get('hdl', 999) < 40:
            score += 2
            factors.append('Low HDL')
        if data.get('triglycerides', 0) > 200:
            score += 1
            factors.append('High triglycerides')
        
        # Age factor
        if context and context.get('age', 0) > 45:
            score += 1
            factors.append('Age > 45')
        
        if score > 0:
            level = 'high' if score >= 6 else 'moderate' if score >= 3 else 'low'
            return {
                'type': 'cardiovascular',
                'score': score,
                'level': level,
                'factors': factors,
                'percentage': min(score * 10, 100)
            }
        return None
    
    def _calculate_diabetes_risk(self, data, context):
        score = 0
        factors = []
        
        glucose = data.get('glucose', 0)
        if glucose >= 126:
            score += 5
            factors.append(f'Fasting glucose: {glucose} mg/dL')
        elif glucose >= 100:
            score += 3
            factors.append(f'Impaired fasting glucose: {glucose} mg/dL')
        
        if data.get('triglycerides', 0) > 150:
            score += 1
            factors.append('Elevated triglycerides')
        
        if data.get('hdl', 999) < 40:
            score += 1
            factors.append('Low HDL')
        
        if context and context.get('age', 0) > 45:
            score += 1
            factors.append('Age > 45')
        
        if score > 0:
            level = 'high' if score >= 5 else 'moderate' if score >= 3 else 'low'
            return {
                'type': 'diabetes',
                'score': score,
                'level': level,
                'factors': factors,
                'percentage': min(score * 15, 100)
            }
        return None
    
    def _calculate_kidney_risk(self, data):
        score = 0
        factors = []
        
        creatinine = data.get('creatinine', 0)
        if creatinine > 1.5:
            score += 3
            factors.append(f'Elevated creatinine: {creatinine} mg/dL')
        elif creatinine > 1.3:
            score += 1
            factors.append(f'Borderline creatinine: {creatinine} mg/dL')
        
        if score > 0:
            level = 'moderate' if score >= 3 else 'low'
            return {
                'type': 'kidney_disease',
                'score': score,
                'level': level,
                'factors': factors
            }
        return None
    
    def _identify_correlations(self, data):
        correlations = []
        
        # Lipid correlations
        if 'ldl' in data and 'triglycerides' in data:
            if data['ldl'] > 130 and data['triglycerides'] > 150:
                correlations.append({
                    'parameters': ['ldl', 'triglycerides'],
                    'relationship': 'both_elevated',
                    'implication': 'increased_cardiovascular_risk'
                })
        
        # Glucose-lipid correlation
        if 'glucose' in data and 'triglycerides' in data:
            if data['glucose'] > 100 and data['triglycerides'] > 150:
                correlations.append({
                    'parameters': ['glucose', 'triglycerides'],
                    'relationship': 'metabolic_correlation',
                    'implication': 'insulin_resistance_indicator'
                })
        
        return correlations

class Model3_ContextualAnalysis:
    def analyze(self, interpretations, model2_output, context):
        if not context:
            return {'adjustments': [], 'context_applied': False}
        
        age = context.get('age', 0)
        gender = context.get('gender', 'male')
        family_history = context.get('family_history', '')
        
        adjustments = []
        adjusted_risks = []
        
        # Age-based adjustments
        age_adjustments = self._apply_age_adjustments(age, model2_output)
        adjustments.extend(age_adjustments)
        
        # Gender-based adjustments
        gender_adjustments = self._apply_gender_adjustments(gender, interpretations, model2_output)
        adjustments.extend(gender_adjustments)
        
        # Family history adjustments
        if family_history:
            fh_adjustments = self._apply_family_history_adjustments(family_history, model2_output)
            adjustments.extend(fh_adjustments)
        
        # Adjust risk scores based on context
        for risk in model2_output.get('risks', []):
            adjusted_risk = self._adjust_risk_score(risk, age, gender, family_history)
            adjusted_risks.append(adjusted_risk)
        
        return {
            'adjustments': adjustments,
            'adjusted_risks': adjusted_risks,
            'context_applied': True,
            'age_group': self._get_age_group(age),
            'risk_modifiers': self._calculate_risk_modifiers(age, gender, family_history)
        }
    
    def _apply_age_adjustments(self, age, model2_output):
        adjustments = []
        
        if age > 60:
            adjustments.append({
                'type': 'age_related',
                'message': 'Age >60: Increased cardiovascular monitoring recommended',
                'priority': 'high'
            })
        elif age > 45:
            adjustments.append({
                'type': 'age_related',
                'message': 'Age >45: Regular cardiovascular screening advised',
                'priority': 'moderate'
            })
        
        if age > 40:
            for pattern in model2_output.get('patterns', []):
                if pattern['name'] == 'prediabetes':
                    adjustments.append({
                        'type': 'age_diabetes',
                        'message': 'Age >40 with prediabetes: Annual HbA1c testing recommended',
                        'priority': 'high'
                    })
        
        return adjustments
    
    def _apply_gender_adjustments(self, gender, interpretations, model2_output):
        adjustments = []
        
        if gender == 'female':
            hdl_value = None
            for param, info in interpretations.items():
                if param == 'hdl':
                    hdl_value = info['value']
                    break
            
            if hdl_value and hdl_value < 50:
                adjustments.append({
                    'type': 'gender_specific',
                    'message': 'Female with HDL <50: Higher cardiovascular risk',
                    'priority': 'moderate'
                })
        
        return adjustments
    
    def _apply_family_history_adjustments(self, family_history, model2_output):
        adjustments = []
        fh_lower = family_history.lower()
        
        if 'diabetes' in fh_lower or 'diabetic' in fh_lower:
            adjustments.append({
                'type': 'family_history',
                'message': 'Family history of diabetes: Enhanced glucose monitoring',
                'priority': 'high'
            })
        
        if 'heart' in fh_lower or 'cardiac' in fh_lower or 'cardiovascular' in fh_lower:
            adjustments.append({
                'type': 'family_history',
                'message': 'Family history of heart disease: Aggressive lipid management',
                'priority': 'high'
            })
        
        if 'kidney' in fh_lower or 'renal' in fh_lower:
            adjustments.append({
                'type': 'family_history',
                'message': 'Family history of kidney disease: Regular renal function monitoring',
                'priority': 'moderate'
            })
        
        return adjustments
    
    def _adjust_risk_score(self, risk, age, gender, family_history):
        adjusted = risk.copy()
        modifier = 1.0
        
        # Age modifier
        if age > 60:
            modifier *= 1.3
        elif age > 45:
            modifier *= 1.15
        
        # Family history modifier
        if family_history:
            fh_lower = family_history.lower()
            if risk['type'] == 'cardiovascular' and ('heart' in fh_lower or 'cardiac' in fh_lower):
                modifier *= 1.5
            elif risk['type'] == 'diabetes' and 'diabetes' in fh_lower:
                modifier *= 1.4
        
        adjusted['original_score'] = risk['score']
        adjusted['adjusted_score'] = round(risk['score'] * modifier, 1)
        adjusted['modifier'] = round(modifier, 2)
        
        # Re-evaluate level based on adjusted score
        if risk['type'] == 'cardiovascular':
            adjusted['level'] = 'high' if adjusted['adjusted_score'] >= 6 else 'moderate' if adjusted['adjusted_score'] >= 3 else 'low'
        elif risk['type'] == 'diabetes':
            adjusted['level'] = 'high' if adjusted['adjusted_score'] >= 5 else 'moderate' if adjusted['adjusted_score'] >= 3 else 'low'
        
        return adjusted
    
    def _get_age_group(self, age):
        if age < 18: return 'pediatric'
        elif age < 45: return 'young_adult'
        elif age < 65: return 'middle_aged'
        else: return 'senior'
    
    def _calculate_risk_modifiers(self, age, gender, family_history):
        modifiers = {'age': 1.0, 'gender': 1.0, 'family_history': 1.0}
        
        if age > 60: modifiers['age'] = 1.3
        elif age > 45: modifiers['age'] = 1.15
        
        if family_history:
            modifiers['family_history'] = 1.4
        
        return modifiers
