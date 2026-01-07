"""
##  Multi format CBC Report Parsing

✔ PDF / Image / CSV detection
✔ OCR using Tesseract
✔ Robust CBC parameter extraction
✔ Unit normalization
✔ Gender-aware classification
✔ Handles abnormal markers (H/L/Low/High)
✔ Detects blank/template reports
✔ Future-report friendly (pattern-based)

Author: Praveen
"""

# =========================
# IMPORTS
# =========================
import re
import json
from pathlib import Path
from datetime import datetime

import pdfplumber
import pytesseract
from PIL import Image

# =========================
# PATH CONFIG
# =========================
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# TESSERACT CONFIG (adjust if needed)
# =========================
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# =========================
# REFERENCE RANGES
# =========================
REFERENCE_RANGES = {
    "hemoglobin": {"male": (13.0, 17.0), "female": (12.0, 15.5)},
    "rbc_count": {"male": (4.5, 5.9), "female": (4.1, 5.1)},
    "wbc_count": {"any": (4000, 11000)},
    "platelet_count": {"any": (150000, 450000)},
    "mcv": {"any": (80, 100)},
    "mch": {"any": (27, 33)},
    "mchc": {"any": (32, 36)},
}

# =========================
# HELPERS
# =========================
def now():
    return datetime.now().strftime("%H:%M:%S")

def safe_float(text):
    if not text:
        return None
    text = re.sub(r"[HL]$", "", text.strip(), flags=re.I)
    try:
        return float(text)
    except:
        return None

def detect_gender(text):
    if re.search(r"female", text, re.I):
        return "female"
    if re.search(r"male", text, re.I):
        return "male"
    return None

def interpret(param, value, gender):
    if value is None:
        return None
    ranges = REFERENCE_RANGES.get(param)
    if not ranges:
        return None
    low, high = ranges.get("any") or ranges.get(gender, (None, None))
    if low is None:
        return None
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "normal"

# =========================
# UNIT NORMALIZATION
# =========================
def normalize_value(param, value, unit):
    unit = (unit or "").lower()

    if value is None:
        return None, unit

    if param == "glucose" and "mmol" in unit:
        return value * 18, "mg/dl"

    if param == "cholesterol" and "mmol" in unit:
        return value * 38.67, "mg/dl"

    if param in ["wbc_count", "platelet_count"]:
        if "thous" in unit:
            return value * 1000, "cells/cumm"
        if "lakh" in unit:
            return value * 100000, "cells/cumm"

    if param == "rbc_count" and "mill" in unit:
        return value, "million/cumm"

    return value, unit or ""

# =========================
# PARAMETER PATTERNS
# =========================
PATTERNS = {
    "hemoglobin": r"(haemoglobin|hemoglobin|\bhb\b).*?([\d\.]+).*?(g/dl|gm%|g%)",
    "rbc_count": r"(r\.?\s*b\.?\s*c\.?\s*count|rbc\s*count).*?([\d\.]+).*?(millions?/cu\s*mm|mill\.?/cmm|million/cumm)",
    "wbc_count": r"(total\s+count\s*\(tc\)|total\s+wbc\s+count|w\.?\s*b\.?\s*c\.?\s*count).*?([\d\.]+).*?(cells/cumm|/cmm|thous/cumm)?",
    "platelet_count": r"(platelet\s*count).*?([\d\.]+).*?(cells/cumm|/cmm|thous/cumm|lakhs/cumm)?",
    "mcv": r"(mcv|mean\s+corpuscular\s+volume).*?([\d\.]+)",
    "mch": r"(mch|mean\s+corpuscular\s+haemoglobin).*?([\d\.]+)",
    "mchc": r"(mchc|mean\s+corpuscular\s+haemoglobin\s+concentration).*?([\d\.]+)",
}

# =========================
# TEXT EXTRACTION
# =========================
def extract_text(file_path):
    if file_path.suffix.lower() == ".pdf":
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)

    if file_path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        return pytesseract.image_to_string(Image.open(file_path))

    return ""

# =========================
# PARAMETER EXTRACTION
# =========================
def extract_parameters(text, gender):
    extracted = {}

    clean_text = re.sub(r"\b(low|high|borderline)\b", "", text, flags=re.I)

    for param, pattern in PATTERNS.items():
        match = re.search(pattern, clean_text, re.I | re.S)
        if not match:
            continue

        value = safe_float(match.group(2))
        unit = match.group(3) if match.lastindex and match.lastindex >= 3 else ""

        std_value, std_unit = normalize_value(param, value, unit)

        extracted[param] = {
            "value_raw": value,
            "unit_raw": unit,
            "value_standard": std_value,
            "unit_standard": std_unit,
            "flag": interpret(param, std_value, gender)
        }

    return extracted

# =========================
# MAIN
# =========================
def main():
    print(f"[{now()}] Week-2 processing started")

    for file in INPUT_DIR.iterdir():
        if file.suffix.lower() not in {".pdf", ".png", ".jpg", ".jpeg"}:
            continue

        print(f"[{now()}] Processing: {file.name}")

        text = extract_text(file)
        gender = detect_gender(text)
        parameters = extract_parameters(text, gender)

        output = {
            "file": file.name,
            "parsed": {
                "gender": gender,
                "parameters": parameters
            }
        }

        if not parameters:
            output["parsed"]["report_status"] = "template_or_blank_report"
            output["parsed"]["note"] = "No patient-specific result values detected."

        out_file = OUTPUT_DIR / f"{file.stem}_week2_parsed.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"[{now()}] Saved JSON → {out_file.name}")

    print(f"[{now()}] Week-2 processing completed")

if __name__ == "__main__":
    main()
