"""
Mahesh / Week2 / data_extraction_mahesh_v2.py

Week-2: OCR & multi-format lab report parsing (STABLE VERSION)

✔ PDF + Image + CSV
✔ OCR using Tesseract
✔ Extracts Hb, Glucose, Cholesterol, RBC, Platelets
✔ Converts units
✔ Interprets values (low / normal / high)
✔ SAFE logging (no Unicode console crashes)
✔ Pipeline-ready (Week-6 compatible)

Run:
    cd "M:\\mahesh\\Intenships\\Infosys Internship"
    . .\\.venv\\Scripts\\Activate.ps1
    python "Mahesh\\Week2\\data_extraction_mahesh_v2.py"
"""

# ==================================================
# SAFE CONSOLE CONFIG (VERY IMPORTANT)
# ==================================================
import sys
sys.stdout.reconfigure(encoding="utf-8")

# ==================================================
# IMPORTS
# ==================================================
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple
import re
import json

import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image

# ==================================================
# TESSERACT CONFIG
# ==================================================
pytesseract.pytesseract.tesseract_cmd = (
    r"M:\mahesh\Intenships\Infosys Internship\Tesseract-OCR\tesseract.exe"
)

# ==================================================
# PATHS
# ==================================================
REPO_ROOT = Path(".").resolve()

WEEK2_ROOT = REPO_ROOT / "Mahesh" / "Week2"
REPORTS_DIR = WEEK2_ROOT / "data" / "testdata"

OUTPUT_DIR = WEEK2_ROOT / "output"
ROW_REPORTS_DIR = OUTPUT_DIR / "row_reports"
UNSUPPORTED_LOG = OUTPUT_DIR / "unsupported_files_log.json"

ROW_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_PDF_EXT = {".pdf"}
SUPPORTED_IMAGE_EXT = {".png", ".jpg", ".jpeg"}
SUPPORTED_CSV_EXT = {".csv"}

# ==================================================
# HELPERS
# ==================================================
def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def try_float(x):
    try:
        if x is None:
            return None
        s = str(x).strip().replace(",", "")
        m = re.match(r"[-+]?\d+(\.\d+)?", s)
        return float(m.group(0)) if m else None
    except Exception:
        return None

# ==================================================
# REFERENCE RANGES (MODEL-1)
# ==================================================
REFERENCE_RANGES = {
    "hemoglobin": {"male": (13.0, 17.0), "female": (12.0, 15.5)},
    "glucose": {"any": (70, 99)},
    "cholesterol": {"any": (0, 200)},
    "rbc_count": {"male": (4.5, 5.5), "female": (4.2, 5.4)},
    "platelet_count": {"any": (150000, 410000)},
}

def interpret_param(param: str, value: float | None) -> str | None:
    if value is None:
        return None
    ranges = REFERENCE_RANGES.get(param)
    if not ranges:
        return None
    low, high = ranges.get("any", list(ranges.values())[0])
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "normal"

# ==================================================
# UNIT NORMALIZATION
# ==================================================
def convert_value_and_unit(param, value_raw, unit_raw):
    v = try_float(value_raw)
    unit = (unit_raw or "").lower()

    if v is None:
        return None, unit, "no_numeric"

    if param == "glucose" and "mmol" in unit:
        return v * 18, "mg/dL", "mmol_to_mg"
    if param == "cholesterol" and "mmol" in unit:
        return v * 38.67, "mg/dL", "mmol_to_mg"

    if param == "platelet_count" and "lakh" in unit:
        return v * 100000, "cells", "lakh_to_cells"

    return v, unit or "", "as_is"

# ==================================================
# TEXT EXTRACTION
# ==================================================
def extract_text_from_pdf(pdf_path: Path) -> str:
    text_parts = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
    except Exception as e:
        print("    [PDF ERROR]", e)
    return "\n".join(text_parts)

def ocr_image(image_path: Path) -> str:
    try:
        img = Image.open(str(image_path))
        return pytesseract.image_to_string(img, lang="eng")
    except Exception as e:
        print("    [OCR ERROR]", e)
        return ""

# ==================================================
# PARAMETER PARSING
# ==================================================
def parse_parameters_from_text(text: str):
    params = {}

    patterns = {
        "hemoglobin": r"(hemoglobin|hb)[^\d]*([\d\.]+)",
        "glucose": r"(glucose|blood sugar)[^\d]*([\d\.]+)",
        "cholesterol": r"(cholesterol)[^\d]*([\d\.]+)",
        "platelet_count": r"(platelet)[^\d]*([\d\.]+)",
        "rbc_count": r"(rbc)[^\d]*([\d\.]+)",
    }

    for line in text.splitlines():
        for param, regex in patterns.items():
            if param not in params:
                m = re.search(regex, line, re.I)
                if m:
                    params[param] = {
                        "value_raw": m.group(2),
                        "unit_raw": "",
                        "source_line": line.strip()
                    }

    enriched = {}
    for param, info in params.items():
        val_std, unit_std, note = convert_value_and_unit(
            param, info["value_raw"], info["unit_raw"]
        )
        enriched[param] = {
            "value_raw": info["value_raw"],
            "value_standard": val_std,
            "unit_standard": unit_std,
            "flag": interpret_param(param, val_std),
            "conversion_note": note
        }

    return enriched

# ==================================================
# FILE PROCESSORS
# ==================================================
def save_report_json(name, payload):
    out = ROW_REPORTS_DIR / name
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out

def process_pdf(file_path):
    print(f"[{timestamp()}] PDF:", file_path.name)
    text = extract_text_from_pdf(file_path)
    parsed = parse_parameters_from_text(text)
    print("    Parameters found:", list(parsed.keys()))
    save_report_json(
        f"{file_path.stem}_week2_parsed.json",
        {"file": file_path.name, "parsed": parsed}
    )

def process_image(file_path):
    print(f"[{timestamp()}] IMAGE:", file_path.name)
    text = ocr_image(file_path)
    parsed = parse_parameters_from_text(text)
    print("    Parameters found:", list(parsed.keys()))
    save_report_json(
        f"{file_path.stem}_week2_parsed.json",
        {"file": file_path.name, "parsed": parsed}
    )

# ==================================================
# MAIN
# ==================================================
def main():
    print("Week-2 Report Folder:", REPORTS_DIR.resolve())

    if not REPORTS_DIR.exists():
        print("❌ Input folder missing")
        return

    files = list(REPORTS_DIR.iterdir())
    if not files:
        print("❌ No input files found")
        return

    unsupported = []

    for f in files:
        ext = f.suffix.lower()
        if ext in SUPPORTED_PDF_EXT:
            process_pdf(f)
        elif ext in SUPPORTED_IMAGE_EXT:
            process_image(f)
        elif ext in SUPPORTED_CSV_EXT:
            print("CSV detected (handled in Week-1):", f.name)
        else:
            unsupported.append(f.name)

    with open(UNSUPPORTED_LOG, "w", encoding="utf-8") as f:
        json.dump({"unsupported_files": unsupported}, f, indent=2)

    print("\n✅ Week-2 OCR & Parsing COMPLETED")

if __name__ == "__main__":
    main()
