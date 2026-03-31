class SynthesisEngine:
    """Aggregates outputs from all three models into a coherent, structured summary."""

    SEVERITY_ORDER = {'critical': 4, 'high': 3, 'moderate': 2, 'low': 1, 'normal': 0}

    def synthesize(self, interpretations, model2_output, contextual):
        findings_list = self._build_findings_list(interpretations, model2_output, contextual)
        overall_severity = self._compute_overall_severity(findings_list, model2_output, contextual)
        narrative = self._build_narrative(findings_list, model2_output, contextual, overall_severity)

        return {
            'summary': narrative,
            'overall_severity': overall_severity,
            'findings_list': findings_list,
            'interpretations': interpretations,
            'model2_output': model2_output,
            'contextual': contextual
        }

    # ── Finding list ──────────────────────────────────────────────────────────

    def _build_findings_list(self, interpretations, model2_output, contextual):
        findings = []

        # Model 1 – abnormal parameters
        for param, info in interpretations.items():
            if info['status'] != 'normal':
                findings.append({
                    'id': f'param_{param}',
                    'source': 'Model 1 – Parameter Interpretation',
                    'type': 'abnormal_parameter',
                    'parameter': param,
                    'value': info['value'],
                    'status': info['status'],
                    'reference': info['reference'],
                    'severity': 'high' if info['status'] in ('high', 'low') else 'moderate',
                    'description': (
                        f"{param.replace('_', ' ').title()} is {info['status'].upper()} "
                        f"({info['value']} vs reference {info['reference']})"
                    )
                })

        # Model 2 – patterns
        for pattern in model2_output.get('patterns', []):
            severity = 'high' if pattern['confidence'] >= 0.85 else 'moderate'
            findings.append({
                'id': f"pattern_{pattern['name']}",
                'source': 'Model 2 – Pattern Recognition',
                'type': 'pattern',
                'name': pattern['name'],
                'confidence': pattern['confidence'],
                'severity': severity,
                'description': (
                    f"Pattern detected: {pattern['name'].replace('_', ' ').title()} "
                    f"(confidence {pattern['confidence']:.0%})"
                )
            })

        # Model 2 – risks
        for risk in model2_output.get('risks', []):
            findings.append({
                'id': f"risk_{risk['type']}",
                'source': 'Model 2 – Risk Assessment',
                'type': 'risk',
                'risk_type': risk['type'],
                'level': risk['level'],
                'score': risk['score'],
                'factors': risk.get('factors', []),
                'severity': risk['level'],
                'description': (
                    f"{risk['type'].replace('_', ' ').title()} risk is {risk['level'].upper()} "
                    f"(score {risk['score']}). Factors: {', '.join(risk.get('factors', []))}"
                )
            })

        # Model 3 – contextual adjustments
        for adj in contextual.get('adjustments', []):
            findings.append({
                'id': f"ctx_{adj['type']}",
                'source': 'Model 3 – Contextual Analysis',
                'type': 'contextual',
                'priority': adj['priority'],
                'severity': 'high' if adj['priority'] == 'high' else 'moderate',
                'description': adj['message']
            })

        # Sort by severity descending
        findings.sort(key=lambda f: self.SEVERITY_ORDER.get(f['severity'], 0), reverse=True)
        return findings

    # ── Severity ──────────────────────────────────────────────────────────────

    def _compute_overall_severity(self, findings_list, model2_output, contextual):
        adjusted_risks = contextual.get('adjusted_risks', [])
        if any(r.get('level') == 'high' for r in adjusted_risks):
            return 'critical'

        high_count = sum(1 for f in findings_list if f['severity'] in ('high', 'critical'))
        if high_count >= 3:
            return 'high'
        if high_count >= 1:
            return 'moderate'
        if findings_list:
            return 'low'
        return 'normal'

    # ── Narrative ─────────────────────────────────────────────────────────────

    def _build_narrative(self, findings_list, model2_output, contextual, overall_severity):
        if not findings_list:
            return "All evaluated parameters are within normal reference ranges. No significant findings detected."

        parts = []

        # Overall status sentence
        severity_label = {
            'critical': 'critical attention',
            'high': 'significant concern',
            'moderate': 'moderate concern',
            'low': 'minor concern',
            'normal': 'no concern'
        }.get(overall_severity, 'review')
        parts.append(f"Overall assessment indicates {severity_label}.")

        # Abnormal parameters
        abnormal = [f for f in findings_list if f['type'] == 'abnormal_parameter']
        if abnormal:
            high_params = [f['parameter'].replace('_', ' ').title() for f in abnormal if f['status'] == 'high']
            low_params  = [f['parameter'].replace('_', ' ').title() for f in abnormal if f['status'] == 'low']
            if high_params:
                parts.append(f"Elevated: {', '.join(high_params)}.")
            if low_params:
                parts.append(f"Below range: {', '.join(low_params)}.")

        # Patterns
        patterns = [f for f in findings_list if f['type'] == 'pattern']
        if patterns:
            names = [f['name'].replace('_', ' ').title() for f in patterns]
            parts.append(f"Patterns identified: {', '.join(names)}.")

        # Risks
        risks = [f for f in findings_list if f['type'] == 'risk']
        if risks:
            risk_strs = [f"{f['risk_type'].replace('_', ' ').title()} ({f['level']})" for f in risks]
            parts.append(f"Risk assessment: {', '.join(risk_strs)}.")

        # Contextual
        ctx_high = [f for f in findings_list if f['type'] == 'contextual' and f['severity'] == 'high']
        if ctx_high:
            parts.append(f"Context flags: {len(ctx_high)} high-priority contextual factor(s) noted.")

        # Adjusted risks
        adjusted = contextual.get('adjusted_risks', [])
        if adjusted:
            upgrades = [r for r in adjusted if r.get('adjusted_score', 0) > r.get('original_score', 0)]
            if upgrades:
                names = [r['type'].replace('_', ' ').title() for r in upgrades]
                parts.append(f"Risk scores elevated by contextual factors for: {', '.join(names)}.")

        return ' '.join(parts)
