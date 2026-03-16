import json
from models import Model1_ParameterInterpretation, Model2_PatternRecognition, Model3_ContextualAnalysis

def evaluate_risk_plausibility():
    """Evaluate risk scores against medical guidelines"""
    
    # Load synthetic data
    with open('synthetic_test_data.json', 'r') as f:
        test_cases = json.load(f)
    
    model1 = Model1_ParameterInterpretation()
    model2 = Model2_PatternRecognition()
    model3 = Model3_ContextualAnalysis()
    
    plausible_count = 0
    total_count = len(test_cases)
    
    print("=" * 80)
    print("RISK SCORE PLAUSIBILITY EVALUATION")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Case {i}/{total_count}] {test['condition']}")
        print("-" * 80)
        
        interpretations = model1.analyze(test['data'], test['context'])
        model2_output = model2.analyze(test['data'], test['context'])
        contextual = model3.analyze(interpretations, model2_output, test['context'])
        
        # Evaluate plausibility
        plausible = evaluate_case_plausibility(test, model2_output, contextual)
        
        if plausible:
            plausible_count += 1
            print("Plausibility: PLAUSIBLE")
        else:
            print("Plausibility: IMPLAUSIBLE")
    
    # Summary
    print("\n" + "=" * 80)
    print("PLAUSIBILITY SUMMARY")
    print("=" * 80)
    plausibility_rate = (plausible_count / total_count) * 100
    print(f"Plausibility Rate: {plausibility_rate:.1f}% ({plausible_count}/{total_count})")
    print(f"Success Criteria: >90% plausibility")
    print(f"Status: {'PASSED' if plausibility_rate > 90 else 'FAILED'}")
    
    # Save results
    with open('plausibility_results.json', 'w') as f:
        json.dump({
            'plausibility_rate': plausibility_rate,
            'plausible': plausible_count,
            'total': total_count
        }, f, indent=2)

def evaluate_case_plausibility(test, model2_output, contextual):
    """Evaluate if risk scores are plausible based on medical guidelines"""
    
    condition = test['condition'].lower()
    data = test['data']
    risks = model2_output['risks']
    
    print(f"\nData: {data}")
    print(f"Context: Age={test['context']['age']}, Gender={test['context']['gender']}")
    
    # Check if appropriate risks are identified
    if 'metabolic syndrome' in condition:
        has_cv_risk = any(r['type'] == 'cardiovascular' for r in risks)
        has_diabetes_risk = any(r['type'] == 'diabetes' for r in risks)
        if not (has_cv_risk or has_diabetes_risk):
            print("Issue: Metabolic syndrome should trigger CV or diabetes risk")
            return False
    
    if 'diabetes' in condition:
        has_diabetes_risk = any(r['type'] == 'diabetes' for r in risks)
        if not has_diabetes_risk:
            print("Issue: Diabetes condition should trigger diabetes risk")
            return False
        # Check if glucose is appropriately high
        if data.get('glucose', 0) < 100:
            print("Issue: Diabetes with normal glucose is implausible")
            return False
    
    if 'kidney' in condition:
        has_kidney_risk = any(r['type'] == 'kidney_disease' for r in risks)
        if not has_kidney_risk:
            print("Issue: Kidney disease should trigger kidney risk")
            return False
    
    if 'cardiovascular' in condition or 'cholesterol' in condition:
        has_cv_risk = any(r['type'] == 'cardiovascular' for r in risks)
        if not has_cv_risk:
            print("Issue: Cardiovascular condition should trigger CV risk")
            return False
    
    # Validate risk scores are reasonable
    for risk in risks:
        print(f"\nRisk: {risk['type']}")
        print(f"  Score: {risk['score']}, Level: {risk['level']}")
        print(f"  Factors: {', '.join(risk['factors'])}")
        
        # Check score-level consistency
        if risk['type'] == 'cardiovascular':
            if risk['level'] == 'high' and risk['score'] < 6:
                print("  Issue: High CV risk should have score >= 6")
                return False
            if risk['level'] == 'moderate' and (risk['score'] < 3 or risk['score'] >= 6):
                print("  Issue: Moderate CV risk should have score 3-5")
                return False
        
        if risk['type'] == 'diabetes':
            if risk['level'] == 'high' and risk['score'] < 5:
                print("  Issue: High diabetes risk should have score >= 5")
                return False
    
    # Check contextual adjustments
    if contextual.get('adjusted_risks'):
        print(f"\nContextual Adjustments:")
        for adj_risk in contextual['adjusted_risks']:
            print(f"  {adj_risk['type']}: {adj_risk['original_score']} -> {adj_risk['adjusted_score']} (modifier: {adj_risk['modifier']}x)")
            
            # Adjusted score should be higher than original for risk factors
            if adj_risk['modifier'] > 1.0 and adj_risk['adjusted_score'] <= adj_risk['original_score']:
                print("  Issue: Adjusted score should increase with modifier > 1")
                return False
    
    return True

if __name__ == '__main__':
    evaluate_risk_plausibility()
