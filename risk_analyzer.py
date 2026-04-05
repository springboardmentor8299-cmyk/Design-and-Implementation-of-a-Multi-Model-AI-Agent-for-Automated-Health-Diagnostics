class RiskAnalyzer:

    def analyze_patterns(self, components):

        risks = []

        glucose = float(components.get("Glucose",0))
        cholesterol = float(components.get("Cholesterol",0))
        hemoglobin = float(components.get("Hemoglobin",0))
        wbc = float(components.get("WBC",0))

        if glucose > 140:
            risks.append("High Diabetes Risk")

        if cholesterol > 240:
            risks.append("High Cardiovascular Risk")

        if glucose > 126 and cholesterol > 200:
            risks.append("Possible Metabolic Syndrome")

        if hemoglobin < 12:
            risks.append("Possible Anemia")

        if wbc > 11000:
            risks.append("Possible Infection")

        if not risks:
            risks.append("No major risk patterns detected")

        return risks