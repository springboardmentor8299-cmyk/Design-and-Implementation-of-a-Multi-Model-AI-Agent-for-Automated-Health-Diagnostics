import unittest
from src.component_extractor import ComponentExtractor

class TestComponentExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = ComponentExtractor()

    def test_extract_components(self):
        text = "Hemoglobin: 14.5 g/dL\nGlucose: 90 mg/dL\nCholesterol: 180 mg/dL\nRBC: 5.2 million/uL\nWBC: 7.0 thousand/uL"
        components = self.extractor.extract_components(text)
        expected = {
            'hemoglobin': 14.5,
            'glucose': 90,
            'cholesterol': 180,
            'RBC': 5.2,
            'WBC': 7.0
        }
        self.assertEqual(components, expected)

    def test_get_component_levels(self):
        text = "Hemoglobin: 14.5 g/dL\nGlucose: 90 mg/dL\nCholesterol: 180 mg/dL\nRBC: 5.2 million/uL\nWBC: 7.0 thousand/uL"
        self.extractor.extract_components(text)
        levels = self.extractor.get_component_levels()
        expected_levels = {
            'hemoglobin': 14.5,
            'glucose': 90,
            'cholesterol': 180,
            'RBC': 5.2,
            'WBC': 7.0
        }
        self.assertEqual(levels, expected_levels)

if __name__ == '__main__':
    unittest.main()