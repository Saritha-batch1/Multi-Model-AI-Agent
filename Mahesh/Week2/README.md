Week-2 – OCR & Multi-Format Report Parsing (Mahesh)

Goal of Week-2
    Extend the Week-1 data ingestion script so that it can read real medical reports in different formats (PDF + images + CSV), extract important lab values, and classify them as Low / Normal / High using simple medical reference ranges.

What I implemented:
1.Multi-format file handling
    The script now automatically detects file types:
        .pdf → processed with pdfplumber
        .png, .jpg, .jpeg → processed with Tesseract OCR
        .csv → treated as a dataset (shape/columns summary, detailed cleaning in Week-1)
    For every supported file, the script generates a JSON report in:
     Mahesh/Week2/output/row_reports/…_week2_parsed.json

2.OCR for image-based reports (Tesseract)
    For each image:
        Run OCR to get raw text.
        Parse that text to extract:
            Hemoglobin (Hb)
            RBC Count
            Platelet Count
            Glucose
            Cholesterol
3.PDF parsing
    For each PDF report: Use pdfplumber to extract text page by page.
    Apply regex patterns to detect lines that look like:
        Haemoglobin 15 g/dL 12–16
        RBC Count 4.75 10~12/L
        Platelet Count 160 10~9/L 150–410
        Glucose (Fasting) 102 mg/dL 74–99
        Cholesterol 154 mg/dL < 200
    Store the original line (source_line) for traceability.

4.Parameter normalisation + unit converson
    For each recognised parameter, I store:
        value_raw – what appears in the report
        unit_raw – unit as detected from the text (e.g., g/dl, mg/dL, mmol/L, lakhs/cumm)
    Convert to a standard unit and value:
    Examples:
        Glucose: 5.36 mmol/L → 96.48 mg/dL
        Cholesterol: mmol/L → mg/dL using factor 38.67
        Platelets: 3.5 lakhs/cumm → 350000 cells
        Hemoglobin: Normalised to g/dL

5.Low / Normal / High classification
   Used simple reference ranges (can be improved later):
        Hemoglobin (female): 12.0–15.5 g/dL
        Glucose (fasting): 70–99 mg/dL
        Cholesterol (total): 0–200 mg/dL
        RBC Count: 4.2–5.5 million/cumm
        Platelets: 150000–410000 cells
    After conversion, each parameter gets a flag:
        "low" / "normal" / "high"
    Store the original line (source_line) for traceability.

6. CSV awareness (link to Week-1)
    If a .csv file is found in Week-2 testdata:
    The script reads it using pandas and prints:
        number of rows
        number of columns
        column names
    No parmeter interpretation for CSV in Week-2, because detailed CSV interpretation is not required.

7. Low / Normal / High classification
    Used simple reference ranges (can be improved later):

8.Logging & robustness
    For every processed PDF/image, one JSON file is saved:
        …_week2_parsed.json under Mahesh/Week2/output/row_reports/
    Unsupported file types (if any) are tracked i
Mahesh/Week2/output/unsupported_files_log.json
Script prints clear logs so we can see:
Which file is being processed
How many characters were extracted
Which parameters were found
Final interpretation