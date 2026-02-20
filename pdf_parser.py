from pypdf import PdfReader


class PdfParser:
    def parse_pdf(self, pdf_file):
        # Logic to parse the PDF and extract text
        text = self.extract_text(pdf_file)
        return text

    def extract_text(self, pdf_file):
        # Logic to extract text from the PDF file
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")