# Week-2: Multi format CBC Report Parsing

## Intern Name
Praveen

## Week
Week-2

---

## Objective
The goal of Week-2 is to extend the Week-1 data ingestion pipeline so that it can process real medical laboratory reports in multiple formats (PDF, images, CSV), extract key Complete Blood Count (CBC) parameters, normalize units, and classify values as Low / Normal / High using simple medical reference ranges.

---

## Scope of Work
- PDF medical reports
- Image-based lab reports using OCR
- CSV awareness (detailed handling covered in Week-1)

---

## Key Features Implemented
- Multi-format file detection
- OCR using Tesseract
- PDF parsing using pdfplumber
- Robust CBC parameter extraction
- Unit normalization
- Gender-aware interpretation
- Abnormal marker handling
- Template / blank report detection

---

## Extracted Parameters
- Hemoglobin
- RBC Count
- WBC Count / Total Count (TC)
- Platelet Count
- PCV / Hematocrit
- MCV
- MCH
- MCHC

---

## Output
Each processed report generates a JSON file containing:
- File metadata
- Detected gender
- Extracted parameters
- Normalized values
- Low / Normal / High classification
- Template detection flag (if applicable)

---

## Design Principles
- Pattern-based extraction
- Incremental improvement
- No over-engineering
- Production-safe OCR handling

---

## Week-2 Status
Week-2 is complete and stable.

---

## Next Steps
Week-3 will focus on risk scoring and patient-level analysis.
