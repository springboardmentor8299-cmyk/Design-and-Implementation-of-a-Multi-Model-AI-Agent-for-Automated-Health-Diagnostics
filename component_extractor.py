import re

class ComponentExtractor:

    def extract_components(self, text):

        components = {}

        lines = text.splitlines()

        for line in lines:

            if "Hemoglobin" in line:
                components["Hemoglobin"] = self.extract_value(line)

            elif "Glucose" in line:
                components["Glucose"] = self.extract_value(line)

            elif "Cholesterol" in line:
                components["Cholesterol"] = self.extract_value(line)

            elif "RBC" in line:
                components["RBC"] = self.extract_value(line)

            elif "WBC" in line:
                components["WBC"] = self.extract_value(line)

        return components


    def extract_value(self,line):

        match = re.search(r"\d+\.?\d*", line)

        if match:
            return float(match.group())

        return None