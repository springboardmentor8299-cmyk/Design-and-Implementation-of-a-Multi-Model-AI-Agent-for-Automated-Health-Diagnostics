def generate_explanations(data):

    explanations = []

    if data.get("Glucose", 0) > 140:
        explanations.append("High glucose level indicates risk of diabetes,High glucose levels indicate that your body isn't processing sugar effectively, which serves as a major warning sign for diabetes. When blood sugar remains elevated, it can damage vessels and organs over time, making early monitoring essential for prevention.")

    if data.get("Cholesterol", 0) > 200:
        explanations.append("High cholesterol may increase heart disease risk,Elevated cholesterol leads to plaque buildup in your arteries, narrowing the pathways for blood flow. This restriction increases the risk of heart disease and stroke, as the heart must work harder to circulate blood through a compromised system.")

    if data.get("Hemoglobin", 100) < 13:
        explanations.append("Low hemoglobin suggests anemia,Low hemoglobin means your red blood cells aren't carrying enough oxygen to your tissues, a condition known as anemia. This lack of oxygen typically results in persistent exhaustion, dizziness, and physical weakness.")

    if data.get("WBC", 0) > 11000:
        explanations.append("High WBC count may indicate infection,Low hemoglobin means your red blood cells aren't carrying enough oxygen to your tissues, a condition known as anemia. This lack of oxygen typically results in persistent exhaustion, dizziness, and physical weakness.")

    if not explanations:
        explanations.append("All parameters are within normal range,A high white blood cell (WBC) count acts as a biological alarm, suggesting that your immune system is actively fighting an infection or inflammation. It is the body's natural response to neutralizing harmful bacteria or viruses.")

    return explanations