class SynthesisEngine:

    def generate_summary(self, components, statuses, risks, user_info):

        summary = []

        for comp, status in statuses.items():

            if status == "High":
                summary.append(f"{comp} level is higher than the normal range.")

            elif status == "Low":
                summary.append(f"{comp} level is lower than the recommended range.")

        if not summary:
            summary.append("All measured blood parameters are within normal range.")

        return " ".join(summary)


    def generate_recommendations(self, risks):

        recommendations = []

        if "High Diabetes Risk" in risks:
            recommendations.append("Reduce sugar intake and monitor blood glucose regularly.")

        if "High Cardiovascular Risk" in risks:
            recommendations.append("Adopt a low-fat diet and increase daily physical activity.")

        if "Possible Anemia" in risks:
            recommendations.append("Increase iron-rich foods such as spinach, beetroot, and dates.")

        if "Possible Infection" in risks:
            recommendations.append("Consult a doctor for further diagnostic tests.")

        if "Possible Metabolic Syndrome" in risks:
            recommendations.append("Maintain balanced diet, weight management and regular exercise.")

        if not recommendations:
            recommendations.append("Maintain a healthy lifestyle with balanced nutrition and routine checkups.")

        return recommendations