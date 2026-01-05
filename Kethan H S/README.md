# Multi-Model AI Agent for Automated Health Diagnostics  

## 📌 Project Overview

This project implements a multi-model AI system that automatically analyzes medical blood test reports provided in multiple formats such as PDFs (text-based and scanned), images, plain text, and JSON. The system extracts laboratory parameters, validates them using standard medical reference ranges, identifies abnormal values, detects health-related risk patterns, and optionally refines interpretations using contextual information like age and gender.

The implementation currently fulfills *Week 1 to Week 4 objectives*.


## 🎯 Objectives Achieved (Week 1 – Week 4)

### ✅ Week 1: Data Ingestion
- Supports multiple input formats:
  - Text-based PDF reports
  - Scanned/image-based PDFs using OCR
  - Image files (PNG, JPG, JPEG)
  - Plain text and JSON files
- Automatically selects the best parsing method.
- Uses OCR fallback when embedded text is unavailable.

### ✅ Week 2: Parameter Extraction & Interpretation (Model 1)
- Extracts blood test parameters using robust pattern matching.
- Normalizes units and validates extracted values.
- Compares values against standard medical reference ranges.
- Classifies each parameter into:
  - Normal
  - High / Low
  - Borderline High / Borderline Low
  - Critical High / Critical Low
- Generates a comprehensive, human-readable diagnostic report.

### ✅ Week 3: Pattern Recognition & Risk Assessment (Model 2)
- Analyzes **combinations of parameters** instead of isolated values.
- Uses **rule-based clinical heuristics** (no machine learning training).
- Detects potential health-related risk patterns such as:
  - Dyslipidemia risk
  - Diabetes risk indicators
  - Kidney function abnormalities
  - Liver enzyme abnormalities
- Ensures explainability and safety suitable for internship-level implementation.

### ✅ Week 4: Contextual Analysis (Model 3)
- Incorporates optional user-provided context:
  - Age
  - Gender
- Refines the interpretation of detected patterns based on context.
- Improves relevance of risk assessment without making clinical diagnoses.


## 🧠 System Architecture

Input Report
↓
Universal Input Parser (PDF / OCR / Image / Text)
↓
Data Extraction Engine
↓
Data Validation & Standardization
↓
Model 1 – Parameter Interpretation
↓
Model 2 – Pattern Recognition & Risk Assessment
↓
Model 3 – Contextual Analysis (Optional)
↓
Comprehensive Diagnostic Report

## 🛠 Technologies Used

- Python  
- pdfplumber – PDF text extraction  
- pytesseract – OCR for scanned documents  
- pdf2image – PDF to image conversion  
- Pillow (PIL) – Image processing  
- NumPy & Pandas – Data handling  
- Regular Expressions – Parameter extraction  

## ▶️ How to Run the Project

1. Open the notebook in *Google Colab*.
2. Run all cells in sequence (`Runtime → Run all`).
3. Upload a blood report file when prompted.
4. (Optional) Provide age and gender for contextual analysis.
5. View the generated diagnostic report in the output.


## 📊 Output

The system produces:
- Individual blood parameter classifications
- Detected health-related risk patterns
- Context-aware interpretation notes (if provided)
- A consolidated diagnostic report with medical disclaimers

## ⚠️ Limitations

- The system uses **rule-based logic**, not trained machine learning models.
- It does **not** provide medical diagnoses.
- Lifestyle factors, medication data, and detailed medical history are not considered.
- Results are intended for **educational and analytical purposes only**.

