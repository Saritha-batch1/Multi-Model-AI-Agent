# AI Health Diagnostics Pipeline (PDF → Insights → Reports)

This repository contains my milestone-wise implementation for the **Infosys Springboard AI/ML Internship** project:  
**AI Design and Implementation of a Multi-Model AI Agent for Automated Health Diagnostics**

The pipeline takes **PDF blood report files** as input, extracts key lab parameters, validates and standardizes the data, detects health patterns, generates recommendations, and produces a final report output.

---

## ✅ Milestones Completed

### ✅ Milestone 1: Data Extraction + Validation + Standardization
- Uploaded PDF lab reports in Google Colab
- Extracted text using **pdfplumber + OCR (Tesseract fallback)**
- Extracted key parameters using regex:
  - Hemoglobin, RBC, WBC, Platelets, Glucose, Cholesterol
- Cleaned and standardized values
- Added status columns (low / normal / high / missing)

📌 Output:
- `ms1_validated_standardized_parameters.csv`

---

### ✅ Milestone 2: Pattern Recognition & Contextual Analysis
- Implemented explainable rule-based pattern detection:
  - Possible anemia pattern
  - Elevated glucose pattern
  - Elevated cholesterol pattern
  - Possible infection / inflammation pattern
- Generated pattern analysis results

📌 Output:
- `ms2_pattern_analysis.csv`

---

### ✅ Milestone 3: Synthesis + Recommendation Generation
- Generated final summary based on detected patterns
- Generated recommendations for each patient record (rule-based)

📌 Output:
- `ms3_final_health_recommendations.csv`

---

### ✅ Milestone 4: Risk Scoring + Report Generation (Final Workflow)
- Added **risk scoring and risk category classification**
- Synthesized patient findings into readable insights
- Generated final automated health reports with disclaimer text

📌 Outputs:
- `ms4_final_pipeline_output.csv`
- `ms4_final_health_reports.txt`

---

## 📂 Files Included

| File | Description |
|------|-------------|
| `ms1_validated_standardized_parameters.csv` | Standardized lab data with status columns |
| `ms2_pattern_analysis.csv` | Pattern detection output |
| `ms3_final_health_recommendations.csv` | Final summary + recommendations |
| `ms4_final_pipeline_output.csv` | Risk scores + final integrated output |
| `ms4_final_health_reports.txt` | Patient-wise generated diagnostic reports |
| `.ipynb notebook` | Complete Google Colab pipeline implementation |

---

## 🛠 Tools / Libraries Used
- Python
- Pandas
- Regex (`re`)
- **pdfplumber**
- **Tesseract OCR** (`pytesseract`)
- `pdf2image`
- Google Colab
