Week-1 Work Summary:
- Loaded the given healthcare dataset.
- Cleaned the data by removing empty values and fixing column names.
- Wrote simple rules to check if blood values (example: glucose, hemoglobin) are High, Low, or Normal.
- Saved the cleaned data for next week.

Main Goal:
Understand the data and prepare it for AI analysis in later weeks.


Design And Implementation Of A Multi-Model Ai Agent For Automated Health Diagnostics

Week 1 — Data ingestion & parameter interpretation

1) Short summary (one-liner)
Completed data ingestion and initial rule-based parameter classification for key blood values (glucose, hemoglobin, cholesterol). Created cleaned dataset and notebook with the code and notes.

2) What I added to the repo
data_extraction.ipynb — Notebook: load dataset, clean data, basic column normalization, and simple rule-based classifiers.
cleaned_data.csv — Cleaned version of the dataset used for tests.
notes.md — Short notes about assumptions, column names, and thresholds used.

3) What I did (step-by-step, technical)
Opened the shared dataset ../data/healthcare_dataset.csv and inspected columns and sample rows.
Normalized column names to lowercase and replaced spaces with underscores.
Dropped rows with all key values missing and handled basic NaNs for critical columns.
Implemented simple rule-based classifiers for parameters:
glucose_status: Very High / High / Normal / Low / Unknown
hemoglobin_status: Low / Normal / High / Unknown
cholesterol_status (if present): High / Borderline / Normal / Unknown
Saved cleaned and annotated data to cleaned_data.csv.
Wrote short notes (notes.md) explaining thresholds and assumptions.

4) How to run (commands)
# from repo root (adjust if you run from a different folder)
cd Mahesh/Week1
# open notebook (if you prefer notebook)
jupyter notebook data_extraction.ipynb
# or run the notebook as a script (if converted)
python run_data_extraction.py
# check cleaned file
ls -l cleaned_data.csv

5) Key files & important code snippets
data_extraction.ipynb contains the main code. Example logic used:
# normalize columns
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
# example glucose classifier
def glucose_status(x):
    try:
        x = float(x)
        if x >= 200: return 'Very High'
        if x >= 140: return 'High'
        if x < 70: return 'Low'
        return 'Normal'
    except:
        return 'Unknown'
df['glucose_status'] = df['glucose'].apply(glucose_status)

6) Assumptions & notes
Thresholds used are basic and for initial testing only — they will be refined after discussion or expert guidance.
Some sample reports in the repo have different column names; I normalized them for consistency.
OCR and PDF parsing will be implemented in Week 2 (so for now I worked with CSV data and sample PDFs).

7) What I plan next (Week 2)
Implement PDF parsing + OCR demo using pdfplumber and pytesseract.
Create example parsed JSON for 2 lab report formats.
Add a small helper shared_code/utils.py for parsing and unit-conversion functions.

8) Questions / help needed from mentor
Please confirm if the threshold values used (listed in notes.md) are acceptable for initial testing.
If there is any preferred data dictionary or reference ranges we should follow, please share.

