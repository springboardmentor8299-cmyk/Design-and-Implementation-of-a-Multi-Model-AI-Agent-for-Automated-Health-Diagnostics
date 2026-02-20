import os
from pdf_parser import PdfParser
from component_extractor import ComponentExtractor

def main():
    print("Welcome to the Blood Component Analyzer!")
    pdf_file_path = input("Please enter the path to the PDF file: ")

    if not os.path.isfile(pdf_file_path):
        print("The specified file does not exist. Please try again.")
        return

    # Parse the PDF
    pdf_parser = PdfParser()
    text_content = pdf_parser.parse_pdf(pdf_file_path)

    # Extract blood component levels
    component_extractor = ComponentExtractor()
    components = component_extractor.extract_components(text_content)

    # Display the extracted levels
    print("Extracted Blood Component Levels:")
    for component, level in components.items():
        print(f"{component}: {level}")

if __name__ == "__main__":
    main()