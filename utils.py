def validate_pdf_file(file_path):
    # Check if the file has a .pdf extension
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("The file must be a PDF.")

def format_component_levels(component_levels):
    # Format the component levels into a readable string
    formatted_levels = []
    for component, level in component_levels.items():
        formatted_levels.append(f"{component}: {level}")
    return "\n".join(formatted_levels)