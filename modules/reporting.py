from fpdf import FPDF
from datetime import datetime
from typing import Dict, List, Any
import io

class HealthReportPDF(FPDF):
    def header(self):
        # Logo/Title
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'AI Health Diagnostics Report', 0, 1, 'C')
        self.ln(5)

        # Date
        self.set_font('Arial', 'I', 10)
        current_date = datetime.now().strftime("%B %d, %Y")
        self.cell(0, 5, f'Generated on: {current_date}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, 'Page %s' % self.page_no(), 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 248, 255)  # Light blue background
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

def create_pdf_report(patient_data: Dict, test_results: List[Dict],
                     analysis: Dict, recommendations: Dict) -> bytes:
    """
    Generate a comprehensive PDF health report.

    Args:
        patient_data: Dictionary with patient information
        test_results: List of interpreted test results
        analysis: Dictionary with patterns and organ health
        recommendations: Dictionary with summary and action plan

    Returns:
        PDF as bytes for download
    """
    pdf = HealthReportPDF()
    pdf.add_page()

    # Section 1: Patient Profile
    pdf.chapter_title("Patient Profile")
    pdf.set_font('Arial', '', 11)

    name = patient_data.get('name', 'Not provided')
    age = patient_data.get('age', 'Not provided')
    gender = patient_data.get('gender', 'Not provided')
    medical_history = patient_data.get('medical_history', 'None provided')

    pdf.cell(0, 6, f"Name: {name}", 0, 1)
    pdf.cell(0, 6, f"Age: {age}", 0, 1)
    pdf.cell(0, 6, f"Gender: {gender}", 0, 1)
    pdf.cell(0, 6, f"Medical History: {medical_history}", 0, 1)
    pdf.ln(5)

    # Section 2: Executive Summary
    pdf.chapter_title("Executive Summary")
    summary_text = recommendations.get('summary_text', 'No summary available.')
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(5)

    # Section 3: Flagged Results (High/Low/Critical only)
    pdf.chapter_title("Flagged Test Results")
    pdf.set_font('Arial', '', 10)

    flagged_results = [result for result in test_results
                      if result.get('status') in ['High', 'Low', 'Critical']]

    if flagged_results:
        for result in flagged_results:
            test_name = result.get('test_name', 'Unknown')
            value = result.get('value', 'N/A')
            unit = result.get('unit', '')
            status = result.get('status', 'Unknown')

            # Color coding for status
            if status == 'High':
                status_display = "HIGH"
            elif status == 'Low':
                status_display = "LOW"
            elif status == 'Critical':
                status_display = "CRITICAL"
            else:
                status_display = status

            pdf.cell(0, 6, f"{test_name}: {value} {unit} - {status_display}", 0, 1)
    else:
        pdf.cell(0, 6, "No abnormal results flagged.", 0, 1)

    pdf.ln(5)

    # Section 4: Detailed Analysis
    pdf.chapter_title("Detailed Analysis")

    # Patterns
    patterns = analysis.get('patterns', [])
    if patterns:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "Detected Patterns:", 0, 1)
        pdf.set_font('Arial', '', 10)

        for pattern in patterns:
            condition = pattern.get('condition', 'Unknown')
            severity = pattern.get('severity', 'Unknown')
            evidence = pattern.get('evidence', [])

            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, f"{condition} (Severity: {severity})", 0, 1)
            pdf.set_font('Arial', '', 10)

            for ev in evidence:
                pdf.cell(0, 5, f"- {ev}", 0, 1)
            pdf.ln(2)
    else:
        pdf.cell(0, 6, "No significant patterns detected.", 0, 1)

    # Organ Health
    organ_health = analysis.get('organ_health', {})
    if organ_health:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "Organ Health Assessment:", 0, 1)
        pdf.set_font('Arial', '', 10)

        for organ, status in organ_health.items():
            pdf.cell(0, 6, f"{organ}: {status}", 0, 1)

    pdf.ln(5)

    # Section 5: Action Plan
    pdf.chapter_title("Personalized Action Plan")

    action_items = recommendations.get('recommendations', [])
    if action_items:
        pdf.set_font('Arial', '', 11)
        for i, action in enumerate(action_items, 1):
            pdf.cell(0, 6, f"{i}. {action}", 0, 1)
    else:
        pdf.cell(0, 6, "No specific recommendations available.", 0, 1)

    # Medical Disclaimer (Footer)
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(255, 0, 0)  # Red color
    pdf.cell(0, 8, "IMPORTANT MEDICAL DISCLAIMER", 0, 1, 'C')
    pdf.set_text_color(0, 0, 0)  # Back to black
    pdf.set_font('Arial', '', 9)

    disclaimer = recommendations.get('disclaimer',
        "This report is for informational purposes only and does not constitute medical advice. " +
        "Please consult a qualified healthcare provider for proper interpretation of your test results " +
        "and personalized medical recommendations.")

    pdf.multi_cell(0, 5, disclaimer)

    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')