from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap
from google.colab import files


def synthesize_findings(row):
    findings = []
    if row['FastingGlucose_mgdl'] >= 126:
        findings.append("Possible diabetes (fasting glucose ≥126 mg/dL)")
    elif row['FastingGlucose_mgdl'] >= 100:
        findings.append("Prediabetes range (fasting glucose 100–125 mg/dL)")
    if row['LDL_mgdl'] >= 160:
        findings.append("High LDL cholesterol")
    if row['HDL_mgdl'] < 40:
        findings.append("Low HDL cholesterol")
    if row['Triglycerides_mgdl'] >= 200:
        findings.append("High triglycerides")
    return findings

df['Findings'] = df.apply(synthesize_findings, axis=1)

def generate_recommendations(findings):
    recs = []
    if any("glucose" in f.lower() for f in findings):
        recs.append("Limit refined sugars and sugary drinks")
        recs.append("Increase physical activity")
    if any("cholesterol" in f.lower() or "ldl" in f.lower() or "hdl" in f.lower() for f in findings):
        recs.append("Adopt a heart‑healthy diet rich in fiber")
    if any("triglycerides" in f.lower() for f in findings):
        recs.append("Reduce alcohol and sugar intake")
    if not recs:
        recs.append("Maintain balanced diet, exercise, and routine checkups")
    return recs

df['Recommendations'] = df['Findings'].apply(generate_recommendations)


def print_sample_table(n=5):
    sample = df.sample(n, random_state=123)
    cols = ['PatientID','Age','Gender','FastingGlucose_mgdl','TotalCholesterol_mgdl','LDL_mgdl','HDL_mgdl','Triglycerides_mgdl']
    print(tabulate(sample[cols], headers='keys', tablefmt='github', showindex=False))

print_sample_table(8)


def save_patient_pdf(patient_id):
    row = df[df['PatientID']==patient_id]
    if row.empty:
        raise ValueError(f"No patient found with ID {patient_id}")
    row = row.iloc[0]

    findings = row['Findings'] if isinstance(row['Findings'], list) else []
    recommendations = row['Recommendations'] if isinstance(row['Recommendations'], list) else []

    c = canvas.Canvas(f"report_{patient_id}.pdf", pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Health Report - {patient_id}")
    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Age: {row['Age']}    Gender: {row['Gender']}")
    y -= 20

    metrics = [
        f"Fasting Glucose: {row['FastingGlucose_mgdl']} mg/dL",
        f"Total Cholesterol: {row['TotalCholesterol_mgdl']} mg/dL",
        f"LDL: {row['LDL_mgdl']} mg/dL   HDL: {row['HDL_mgdl']} mg/dL",
        f"Triglycerides: {row['Triglycerides_mgdl']} mg/dL",
        f"Creatinine: {row['Creatinine_mgdl']} mg/dL   Urea: {row['Urea_mgdl']} mg/dL",
        f"TSH: {row['TSH_uIUml']} uIU/mL   Vitamin D: {row['VitaminD_ngml']} ng/mL",
    ]
    for m in metrics:
        c.drawString(50, y, m)
        y -= 18

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Findings:")
    y -= 20
    c.setFont("Helvetica", 11)
    for f in findings[:12]:
        for line in wrap(f, 90):
            c.drawString(60, y, f"- {line}")
            y -= 16
            if y < 80: 
                c.showPage(); y = height - 50; c.setFont("Helvetica", 11)

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Recommendations:")
    y -= 20
    c.setFont("Helvetica", 11)
    for r in recommendations[:10]:
        for line in wrap(r, 90):
            c.drawString(60, y, f"- {line}")
            y -= 16
            if y < 80: 
                c.showPage(); y = height - 50; c.setFont("Helvetica", 11)

    y -= 10
    c.setFont("Helvetica-Oblique", 10)
    disclaimer = "This AI-generated summary provides general information and is not a substitute for professional medical advice."
    for line in wrap(disclaimer, 95):
        c.drawString(50, y, line)
        y -= 14

    c.save()
    return f"report_{patient_id}.pdf"


sample_id = df.sample(1, random_state=7)['PatientID'].iloc[0]
pdf_path = save_patient_pdf(sample_id)
print("✅ Saved:", pdf_path)

files.download(pdf_path)
