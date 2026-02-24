class SynthesisEngine:
    def synthesize(self, interpretations, risks, contextual):
        findings = []
        
        abnormal = [k for k, v in interpretations.items() if v['status'] != 'normal']
        if abnormal:
            findings.append(f"Abnormal parameters detected: {', '.join(abnormal)}")
        
        if risks.get('risks'):
            risk_summary = ', '.join([r['type'] for r in risks['risks']])
            findings.append(f"Risk factors identified: {risk_summary}")
        
        if contextual.get('adjustments'):
            findings.extend(contextual['adjustments'])
        
        return {
            'summary': ' | '.join(findings) if findings else 'All parameters within normal range',
            'interpretations': interpretations,
            'risks': risks,
            'contextual': contextual
        }
