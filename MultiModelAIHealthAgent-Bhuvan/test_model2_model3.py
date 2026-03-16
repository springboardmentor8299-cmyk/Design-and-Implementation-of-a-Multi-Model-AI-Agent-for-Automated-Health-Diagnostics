import json
from models import Model1_ParameterInterpretation, Model2_PatternRecognition, Model3_ContextualAnalysis

# Test cases for Model 2 and Model 3
test_cases = [
    {
        'name': 'Metabolic Syndrome',
        'data': {
            'glucose': 110,
            'triglycerides': 180,
            'hdl': 35,
            'cholesterol_total': 250,
            'ldl': 160
        },
        'context': {'age': 55, 'gender': 'male', 'family_history': 'diabetes, heart disease'},
        'expected_patterns': ['metabolic_syndrome', 'dyslipidemia', 'prediabetes']
    },
    {
        'name': 'High Cardiovascular Risk',
        'data': {
            'cholesterol_total': 280,
            'ldl': 180,
            'hdl': 30,
            'triglycerides': 220,
            'glucose': 95
        },
        'context': {'age': 62, 'gender': 'male', 'family_history': 'heart disease'},
        'expected_patterns': ['dyslipidemia']
    },
    {
        'name': 'Diabetes Indicator',
        'data': {
            'glucose': 135,
            'triglycerides': 200,
            'hdl': 38,
            'hemoglobin': 14.0
        },
        'context': {'age': 48, 'gender': 'male', 'family_history': 'diabetes'},
        'expected_patterns': ['diabetes_indicator', 'dyslipidemia']
    },
    {
        'name': 'Kidney Dysfunction',
        'data': {
            'creatinine': 1.8,
            'glucose': 105,
            'hemoglobin': 11.5
        },
        'context': {'age': 65, 'gender': 'male', 'family_history': 'kidney disease'},
        'expected_patterns': ['kidney_dysfunction', 'prediabetes', 'anemia']
    },
    {
        'name': 'Normal Profile',
        'data': {
            'glucose': 85,
            'cholesterol_total': 180,
            'ldl': 95,
            'hdl': 55,
            'triglycerides': 120,
            'hemoglobin': 14.5
        },
        'context': {'age': 30, 'gender': 'male', 'family_history': ''},
        'expected_patterns': []
    }
]

def run_tests():
    model1 = Model1_ParameterInterpretation()
    model2 = Model2_PatternRecognition()
    model3 = Model3_ContextualAnalysis()
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    print("=" * 80)
    print("MODEL 2 & MODEL 3 EVALUATION")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{total_tests}] {test['name']}")
        print("-" * 80)
        
        # Run Model 1
        interpretations = model1.analyze(test['data'], test['context'])
        
        # Run Model 2
        model2_output = model2.analyze(test['data'], test['context'])
        
        # Run Model 3
        contextual = model3.analyze(interpretations, model2_output, test['context'])
        
        # Evaluate patterns
        detected_patterns = [p['name'] for p in model2_output['patterns']]
        expected_patterns = test['expected_patterns']
        
        pattern_match = all(p in detected_patterns for p in expected_patterns)
        
        print(f"Expected Patterns: {expected_patterns}")
        print(f"Detected Patterns: {detected_patterns}")
        print(f"Pattern Match: {'PASS' if pattern_match else 'FAIL'}")
        
        # Display risks
        if model2_output['risks']:
            print(f"\nRisk Scores:")
            for risk in model2_output['risks']:
                print(f"  - {risk['type']}: Score={risk['score']}, Level={risk['level']}")
                print(f"    Factors: {', '.join(risk['factors'])}")
        
        # Display correlations
        if model2_output['correlations']:
            print(f"\nCorrelations:")
            for corr in model2_output['correlations']:
                print(f"  - {corr['parameters']}: {corr['implication']}")
        
        # Display contextual adjustments
        if contextual.get('adjustments'):
            print(f"\nContextual Adjustments:")
            for adj in contextual['adjustments']:
                print(f"  - [{adj['priority']}] {adj['message']}")
        
        # Display adjusted risks
        if contextual.get('adjusted_risks'):
            print(f"\nAdjusted Risk Scores:")
            for risk in contextual['adjusted_risks']:
                print(f"  - {risk['type']}: {risk['original_score']} -> {risk['adjusted_score']} (modifier: {risk['modifier']}x)")
        
        test_result = {
            'test_name': test['name'],
            'pattern_match': pattern_match,
            'patterns_detected': detected_patterns,
            'risks': model2_output['risks'],
            'contextual_adjustments': len(contextual.get('adjustments', []))
        }
        results.append(test_result)
        
        if pattern_match:
            passed_tests += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    accuracy = (passed_tests / total_tests) * 100
    print(f"Pattern Identification Accuracy: {accuracy:.1f}% ({passed_tests}/{total_tests})")
    print(f"Success Criteria: >85% accuracy")
    print(f"Status: {'PASSED' if accuracy > 85 else 'FAILED'}")
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump({
            'accuracy': accuracy,
            'passed': passed_tests,
            'total': total_tests,
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to test_results.json")

if __name__ == '__main__':
    run_tests()
