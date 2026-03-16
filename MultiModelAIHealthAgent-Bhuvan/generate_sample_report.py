from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

def generate_sample_blood_report():
    filename = "Sample_Blood_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Header
    story.append(Paragraph("MEDICAL LABORATORY", styles['Title']))
    story.append(Paragraph("Blood Test Report", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    story.append(Paragraph("Patient Information", styles['Heading2']))
    patient_data = [
        ['Patient Name:', 'John Doe'],
        ['Age:', '55 years'],
        ['Gender:', 'Male'],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Report ID:', 'BT-2024-001']
    ]
    
    t1 = Table(patient_data, colWidths=[2*inch, 4*inch])
    t1.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 0.3*inch))
    
    # Test Results
    story.append(Paragraph("Laboratory Test Results", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    test_data = [
        ['Test Parameter', 'Result', 'Unit', 'Reference Range'],
        ['Hemoglobin', '14.5', 'g/dL', '13.5-17.5'],
        ['Glucose (Fasting)', '110', 'mg/dL', '70-100'],
        ['Total Cholesterol', '250', 'mg/dL', '0-200'],
        ['LDL Cholesterol', '160', 'mg/dL', '0-100'],
        ['HDL Cholesterol', '35', 'mg/dL', '40-999'],
        ['Triglycerides', '180', 'mg/dL', '0-150'],
        ['Creatinine', '1.0', 'mg/dL', '0.7-1.3'],
        ['WBC Count', '7.5', '10^3/μL', '4.5-11.0'],
        ['Platelet Count', '250', '10^3/μL', '150-400'],
    ]
    
    t2 = Table(test_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.8*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.3*inch))
    
    # Notes
    story.append(Paragraph("Clinical Notes", styles['Heading3']))
    notes = """Patient presents with elevated glucose, total cholesterol, LDL, and triglycerides. 
    HDL is below normal range. Family history of diabetes and cardiovascular disease reported. 
    Recommend follow-up with physician for comprehensive evaluation."""
    story.append(Paragraph(notes, styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("_" * 80, styles['Normal']))
    story.append(Paragraph("Lab Director: Dr. Sarah Johnson, MD", styles['Normal']))
    story.append(Paragraph("Certified Medical Laboratory", styles['Normal']))
    
    doc.build(story)
    print(f"Sample blood report generated: {filename}")

if __name__ == '__main__':
    generate_sample_blood_report()
