import unittest
from src.pdf_parser import PdfParser

class TestPdfParser(unittest.TestCase):

    def setUp(self):
        self.parser = PdfParser()

    def test_parse_pdf_valid(self):
        # Assuming we have a sample PDF file for testing
        result = self.parser.parse_pdf('sample_valid.pdf')
        self.assertIsInstance(result, str)  # Check if the result is a string

    def test_parse_pdf_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_pdf('non_existent_file.pdf')

    def test_extract_text(self):
        text = self.parser.extract_text('sample_valid.pdf')
        self.assertIn('Hemoglobin', text)  # Check if the text contains expected keywords

if __name__ == '__main__':
    unittest.main()