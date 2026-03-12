from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(parameters, risk):

    path = "reports/health_report.pdf"

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Health Diagnostics Report", styles["Title"]))
    elements.append(Paragraph(f"Overall Risk: {risk}", styles["Normal"]))

    for p in parameters:
        elements.append(
            Paragraph(f"{p['name']} : {p['value']} ({p['status']})", styles["Normal"])
        )

    pdf = SimpleDocTemplate(path)
    pdf.build(elements)

    return path