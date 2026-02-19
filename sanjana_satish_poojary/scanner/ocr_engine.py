import pytesseract
from PIL import Image
import pdfplumber

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def scan_pdf(file_path):

    text = ""

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            text += page.extract_text()

    return text



def scan_image(file_path):

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return text
