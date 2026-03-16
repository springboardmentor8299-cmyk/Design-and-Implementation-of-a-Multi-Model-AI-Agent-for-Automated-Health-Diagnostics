class SynthesisEngine:
    def synthesize(self, interpretations, model2_output, contextual):
        findings = []
        
        abnormal = [k for k, v in interpretations.items() if v['status'] != 'normal']
        if abnormal:
            findings.append(f"Abnormal parameters: {', '.join(abnormal)}")
        
        if model2_output.get('patterns'):
            pattern_names = [p['name'] for p in model2_output['patterns']]
            findings.append(f"Patterns identified: {', '.join(pattern_names)}")
        
        if model2_output.get('risks'):
            risk_summary = ', '.join([f"{r['type']} ({r['level']})" for r in model2_output['risks']])
            findings.append(f"Risk assessment: {risk_summary}")
        
        if contextual.get('adjustments'):
            findings.append(f"Contextual adjustments applied: {len(contextual['adjustments'])} factors")
        
        return {
            'summary': ' | '.join(findings) if findings else 'All parameters within normal range',
            'interpretations': interpretations,
            'model2_output': model2_output,
            'contextual': contextual
        }
