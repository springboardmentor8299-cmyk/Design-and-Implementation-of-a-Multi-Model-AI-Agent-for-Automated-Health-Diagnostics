import re

class ComponentExtractor:
    def __init__(self):
        self.component_levels = {}

    def extract_components(self, text):
        if not text:
            return {}

        self.component_levels = {}
        lines = text.splitlines()

        for line in lines:

            if "Hemoglobin" in line:
                self.component_levels['Hemoglobin'] = self._extract_value(line)

            elif "Glucose" in line:
                self.component_levels['Glucose'] = self._extract_value(line)

            elif "Cholesterol" in line:
                self.component_levels['Cholesterol'] = self._extract_value(line)

            elif "RBC" in line:
                self.component_levels['RBC'] = self._extract_value(line)

            elif "WBC" in line:
                self.component_levels['WBC'] = self._extract_value(line)

        return self.component_levels

    def _extract_value(self, line):
        match = re.search(r'\d+\.?\d*', line)
        if match:
            return match.group()
        return None

    def get_component_levels(self):
        return self.component_levels
