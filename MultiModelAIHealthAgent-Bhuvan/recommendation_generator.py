import requests
from config import PRIVATE_API_URL, PRIVATE_API_KEY, MODEL_NAME


class RecommendationGenerator:
    """Generates actionable, finding-linked recommendations from synthesized findings."""

    def __init__(self):
        self.api_url = PRIVATE_API_URL
        self.api_key = PRIVATE_API_KEY
        self.model = MODEL_NAME

    def generate(self, findings):
        """Returns a list of recommendation dicts, each linked to a specific finding."""
        recs = self._generate_rule_based(findings)

        # Attempt LLM enrichment; fall back silently
        try:
            enriched = self._enrich_with_llm(findings, recs)
            if enriched:
                return enriched
        except Exception:
            pass

        return recs

    # ── Rule-based core ───────────────────────────────────────────────────────

    def _generate_rule_based(self, findings):
        recs = []
        seen = set()

        def add(finding_id, category, text):
            key = (finding_id, text[:40])
            if key not in seen:
                seen.add(key)
                recs.append({'finding_id': finding_id, 'category': category, 'advice': text})

        interpretations = findings.get('interpretations', {})
        model2 = findings.get('model2_output', {})
        contextual = findings.get('contextual', {})
        findings_list = findings.get('findings_list', [])

        # ── Parameter-level recommendations ──────────────────────────────────
        for param, info in interpretations.items():
            fid = f'param_{param}'
            status = info['status']

            if param == 'glucose':
                if status == 'high':
                    add(fid, 'diet',      'Limit refined carbohydrates, sugary drinks, and processed foods to manage elevated glucose.')
                    add(fid, 'lifestyle', 'Aim for 150 min/week of moderate aerobic exercise (e.g., brisk walking) to improve insulin sensitivity.')
                    add(fid, 'follow_up', 'Request HbA1c test to assess 3-month average glucose control.')

            elif param == 'cholesterol_total':
                if status == 'high':
                    add(fid, 'diet',      'Adopt a heart-healthy diet: increase soluble fibre (oats, legumes), reduce saturated and trans fats.')
                    add(fid, 'lifestyle', 'Engage in regular aerobic activity; even 30 min/day of walking can lower LDL by ~5–10%.')
                    add(fid, 'follow_up', 'Repeat full lipid panel in 3 months; discuss statin therapy with your physician if levels remain elevated.')

            elif param == 'ldl':
                if status == 'high':
                    add(fid, 'diet',      'Replace saturated fats (red meat, full-fat dairy) with unsaturated fats (olive oil, nuts, avocado).')
                    add(fid, 'follow_up', 'Discuss LDL-lowering medication (statin or ezetimibe) with your cardiologist.')

            elif param == 'hdl':
                if status == 'low':
                    add(fid, 'diet',      'Increase omega-3 rich foods (fatty fish, flaxseed, walnuts) to raise HDL cholesterol.')
                    add(fid, 'lifestyle', 'Quit smoking if applicable; smoking is a leading cause of low HDL.')
                    add(fid, 'lifestyle', 'Regular vigorous exercise (cycling, swimming) is one of the most effective ways to raise HDL.')

            elif param == 'triglycerides':
                if status == 'high':
                    add(fid, 'diet',      'Eliminate sugary beverages and alcohol; reduce simple carbohydrates to lower triglycerides.')
                    add(fid, 'diet',      'Increase dietary omega-3 fatty acids (salmon, mackerel, fish oil supplements).')
                    add(fid, 'follow_up', 'Recheck triglycerides after 6–8 weeks of dietary changes.')

            elif param == 'hemoglobin':
                if status == 'low':
                    add(fid, 'diet',      'Increase iron-rich foods (lean red meat, spinach, lentils) and pair with vitamin C to enhance absorption.')
                    add(fid, 'diet',      'Consider iron or B12/folate supplementation after confirming deficiency type with your doctor.')
                    add(fid, 'follow_up', 'Request CBC with iron studies and ferritin to identify the cause of anaemia.')

            elif param == 'creatinine':
                if status == 'high':
                    add(fid, 'diet',      'Maintain adequate hydration (2–3 L water/day); limit high-protein diet and NSAIDs.')
                    add(fid, 'follow_up', 'Consult a nephrologist; request eGFR and urine albumin-to-creatinine ratio.')
                    add(fid, 'follow_up', 'Monitor blood pressure closely — hypertension accelerates kidney decline.')

        # ── Pattern-level recommendations ─────────────────────────────────────
        pattern_names = {p['name'] for p in model2.get('patterns', [])}

        if 'metabolic_syndrome' in pattern_names:
            fid = 'pattern_metabolic_syndrome'
            add(fid, 'diet',      'Follow a Mediterranean-style diet: whole grains, vegetables, lean protein, and healthy fats.')
            add(fid, 'lifestyle', 'Target 5–7% body weight reduction if overweight; this significantly reduces metabolic syndrome markers.')
            add(fid, 'follow_up', 'Schedule a comprehensive metabolic panel and waist circumference measurement with your GP.')

        if 'dyslipidemia' in pattern_names:
            fid = 'pattern_dyslipidemia'
            add(fid, 'diet',      'Avoid trans fats entirely; read food labels for "partially hydrogenated oils".')
            add(fid, 'follow_up', 'Discuss cardiovascular risk stratification and possible lipid-lowering therapy with your physician.')

        if 'prediabetes' in pattern_names:
            fid = 'pattern_prediabetes'
            add(fid, 'diet',      'Reduce glycaemic load: choose low-GI foods (legumes, non-starchy vegetables, whole grains).')
            add(fid, 'lifestyle', 'Structured lifestyle intervention (diet + exercise) can reduce progression to diabetes by ~58%.')
            add(fid, 'follow_up', 'Annual fasting glucose and HbA1c monitoring is essential.')

        if 'diabetes_indicator' in pattern_names:
            fid = 'pattern_diabetes_indicator'
            add(fid, 'follow_up', 'Confirm diabetes diagnosis with a repeat fasting glucose or oral glucose tolerance test.')
            add(fid, 'follow_up', 'Refer to an endocrinologist or diabetes educator for a management plan.')
            add(fid, 'diet',      'Work with a dietitian to create a personalised carbohydrate-controlled meal plan.')

        if 'kidney_dysfunction' in pattern_names:
            fid = 'pattern_kidney_dysfunction'
            add(fid, 'diet',      'Limit dietary phosphorus (processed foods, cola drinks) and potassium if advised by your nephrologist.')
            add(fid, 'follow_up', 'Urgent nephrology referral; monitor eGFR trend every 3 months.')

        if 'anemia' in pattern_names:
            fid = 'pattern_anemia'
            add(fid, 'diet',      'Increase haem iron intake (lean meat, poultry) and non-haem iron (fortified cereals, dark leafy greens).')
            add(fid, 'follow_up', 'Investigate underlying cause (iron deficiency, B12/folate deficiency, chronic disease).')

        # ── Risk-level recommendations ─────────────────────────────────────────
        for risk in model2.get('risks', []):
            fid = f"risk_{risk['type']}"
            level = risk['level']

            if risk['type'] == 'cardiovascular':
                if level in ('high', 'moderate'):
                    add(fid, 'lifestyle', 'Stop smoking and limit alcohol to ≤1 drink/day to reduce cardiovascular risk.')
                    add(fid, 'follow_up', 'Discuss aspirin therapy and statin use with your cardiologist based on 10-year CVD risk score.')
                if level == 'high':
                    add(fid, 'follow_up', 'Arrange stress ECG or coronary calcium scoring to assess subclinical atherosclerosis.')

            if risk['type'] == 'diabetes':
                if level in ('high', 'moderate'):
                    add(fid, 'lifestyle', 'Maintain a healthy weight; even modest weight loss (5–10%) substantially lowers diabetes risk.')
                    add(fid, 'follow_up', 'Enrol in a structured diabetes prevention programme if available in your area.')

            if risk['type'] == 'kidney_disease':
                add(fid, 'follow_up', 'Control blood pressure to <130/80 mmHg; ACE inhibitors or ARBs are preferred in CKD.')
                add(fid, 'diet',      'Moderate protein intake (0.8 g/kg/day) to reduce kidney workload.')

        # ── Contextual recommendations ─────────────────────────────────────────
        adjusted_risks = contextual.get('adjusted_risks', [])
        for risk in adjusted_risks:
            if risk.get('modifier', 1.0) > 1.2:
                fid = f"ctx_{risk['type']}"
                add(fid, 'follow_up',
                    f"Given your personal risk profile, {risk['type'].replace('_', ' ')} risk is elevated "
                    f"(adjusted score: {risk['adjusted_score']}). More frequent monitoring is advised.")

        for adj in contextual.get('adjustments', []):
            if adj['priority'] == 'high':
                fid = f"ctx_{adj['type']}"
                add(fid, 'follow_up', adj['message'])

        # ── Fallback ──────────────────────────────────────────────────────────
        if not recs:
            recs.append({
                'finding_id': 'general',
                'category': 'lifestyle',
                'advice': 'All parameters are within normal range. Maintain a balanced diet, regular exercise, and annual health check-ups.'
            })

        return recs

    # ── LLM enrichment (optional) ─────────────────────────────────────────────

    def _enrich_with_llm(self, findings, rule_recs):
        summary = findings.get('summary', '')
        rule_text = '\n'.join(f"- [{r['category'].upper()}] {r['advice']}" for r in rule_recs)

        prompt = (
            f"A patient's blood report has been analysed. Summary:\n{summary}\n\n"
            f"Rule-based recommendations already generated:\n{rule_text}\n\n"
            "Review these recommendations for accuracy and add any important missing advice. "
            "Return the final list in the same format: - [CATEGORY] advice. "
            "Do NOT remove existing recommendations. Keep it concise and clinically sound."
        )

        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        response = requests.post(
            self.api_url,
            json={'model': self.model, 'prompt': prompt, 'stream': False},
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            return None

        llm_text = response.json().get('response', '')
        if not llm_text:
            return None

        # Parse LLM output back into structured list
        enriched = list(rule_recs)  # keep originals
        for line in llm_text.splitlines():
            line = line.strip()
            if line.startswith('- [') and ']' in line:
                bracket_end = line.index(']')
                category = line[3:bracket_end].lower()
                advice = line[bracket_end + 1:].strip().lstrip(':').strip()
                if advice and not any(r['advice'] == advice for r in enriched):
                    enriched.append({'finding_id': 'llm_enriched', 'category': category, 'advice': advice})

        return enriched if len(enriched) > len(rule_recs) else None
