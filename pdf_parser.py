from pypdf import PdfReader

class PdfParser:

    def parse_pdf(self, pdf_file):

        reader = PdfReader(pdf_file)

        text = ""

        for page in reader.pages:
            text += page.extract_text()

        return text