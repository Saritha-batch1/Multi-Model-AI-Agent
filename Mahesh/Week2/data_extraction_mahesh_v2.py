"""
Uses your current folder structure (Mahesh/Week2/data/testdata)
Handles PDF + images (.png/.jpg/.jpeg) + CSV
Uses Tesseract OCR (with your local path)
Extracts Hb / RBC / Platelet / Glucose / Cholesterol
Converts units (mmol/L → mg/dL, lakh → cells, etc.)
Interprets values as low / normal / high
Saves per-file JSON reports under Mahesh/Week2/output/row_reports
Supported input file types (for reports):
- PDF:       .pdf
- Images:    .jpg, .jpeg, .png, .bmp, .tif, .tiff
- Word:      .docx
- Text:      .txt
- Excel:     .xlsx  (tabular lab exports)
Unsupported types (audio/video/archives/executables/etc.) are detected
and reported as clear errors.
"""

"""
Mahesh / Week2 / data_extraction_mahesh_v2.py

Week-2: OCR & multi-format lab report parsing

Run from repo root:
    cd "M:\\mahesh\\Intenships\\Infosys Internship"
    . .\.venv\Scripts\Activate.ps1
    python "Mahesh\\Week2\\data_extraction_mahesh_v2.py"
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple
import re
import json

import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image

try:
    import docx  # for .docx Word files (future use)
except ImportError:
    docx = None

# ---------- CONFIG: Tesseract path (you already installed here)
pytesseract.pytesseract.tesseract_cmd = (
    r"M:\mahesh\Intenships\Infosys Internship\Tesseract-OCR\tesseract.exe"
)

# ---------- PATHS (adapted to your repo layout)
REPO_ROOT = Path(".").resolve()

WEEK2_ROOT = REPO_ROOT / "Mahesh" / "Week2"
REPORTS_DIR = WEEK2_ROOT / "data" / "testdata"

OUTPUT_DIR = WEEK2_ROOT / "output"
ROW_REPORTS_DIR = OUTPUT_DIR / "row_reports"
UNSUPPORTED_LOG = OUTPUT_DIR / "unsupported_files_log.json"

ROW_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# what types are treated as medical docs in Week-2
SUPPORTED_PDF_EXT = {".pdf"}
SUPPORTED_IMAGE_EXT = {".png", ".jpg", ".jpeg"}
SUPPORTED_CSV_EXT = {".csv"}  # handled, but not lab-parameter interpreted yet


# ---------- Small helpers
def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def try_float(x) -> float | None:
    try:
        if x is None:
            return None
        s = str(x).strip().replace(",", "")
        m = re.match(r"[-+]?\d+(\.\d+)?", s)
        return float(m.group(0)) if m else None
    except Exception:
        return None


# ---------- Reference ranges (simple rules)
REFERENCE_RANGES = {
    "hemoglobin": {"male": (13.0, 17.0), "female": (12.0, 15.5)},
    "glucose": {"any": (70, 99)},  # fasting mg/dL
    "cholesterol": {"any": (0, 200)},  # total mg/dL
    "rbc_count": {"male": (4.5, 5.5), "female": (4.2, 5.4)},  # million/cumm
    "platelet_count": {"any": (150000, 410000)},  # cells
}


def interpret_param(param: str, value: float | None, sex: str = "any") -> str | None:
    if value is None:
        return None

    ranges = REFERENCE_RANGES.get(param)
    if not ranges:
        return None

    if sex and sex.lower() in ranges:
        low, high = ranges[sex.lower()]
    elif "any" in ranges:
        low, high = ranges["any"]
    else:
        low, high = list(ranges.values())[0]

    if value < low:
        return "low"
    if value > high:
        return "high"
    return "normal"


# ---------- Unit conversion
def normalize_unit(unit_raw: str | None) -> str:
    if not unit_raw:
        return ""
    u = unit_raw.strip().lower()
    u = u.replace(" ", "")
    u = u.replace("mg/dl", "mg/dl")
    u = u.replace("g/dl", "g/dl")
    u = u.replace("mmol/l", "mmol/l")
    return u


def convert_value_and_unit(
    param: str, value_raw: str | float | None, unit_raw: str | None
) -> Tuple[float | None, str, str]:
    """
    Return (value_standard, unit_standard, conversion_note)
    """
    v = try_float(value_raw)
    unit_raw_norm = normalize_unit(unit_raw)

    if v is None:
        return None, unit_raw_norm, "no_numeric_value"

    # default: use as-is
    value_std = v
    unit_std = unit_raw_norm or ""
    note = "used_as_is"

    # Glucose conversions
    if param == "glucose":
        if "mmol/l" in unit_raw_norm:
            value_std = v * 18.0
            unit_std = "mg/dL"
            note = "converted_from_mmol_per_l"
        else:
            unit_std = "mg/dL"

    # Cholesterol conversions
    elif param == "cholesterol":
        if "mmol/l" in unit_raw_norm:
            value_std = v * 38.67
            unit_std = "mg/dL"
            note = "converted_from_mmol_per_l"
        else:
            unit_std = "mg/dL"

    # Platelets conversions
    elif param == "platelet_count":
        if "lakh" in unit_raw_norm or "lac" in unit_raw_norm:
            value_std = v * 100000.0
            unit_std = "cells"
            note = "converted_from_lakh"
        elif "10~9/l" in unit_raw_norm or "10^9/l" in unit_raw_norm:
            # leave as-is but still treat as cells for interpretation
            unit_std = "cells"
            note = "approx_10e9_per_l_as_cells"
        else:
            unit_std = "cells"

    # Hb & RBC – keep units but normalize
    elif param == "hemoglobin":
        unit_std = "g/dL"
    elif param == "rbc_count":
        unit_std = ""

    return value_std, unit_std, note


# ---------- Text extraction
def extract_text_from_pdf(pdf_path: Path) -> str:
    text_parts: list[str] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    print(f"    - Page {i}: pdfplumber text")
                text_parts.append(page_text)
    except Exception as e:
        print("    [ERROR] pdfplumber error:", e)
    text = "\n".join(text_parts)
    if text.strip():
        print(f"    → Extracted {len(text)} characters from PDF")
    else:
        print("    [WARN] No text extracted from PDF")
    return text


def ocr_image(image_path: Path) -> str:
    try:
        img = Image.open(str(image_path))
    except Exception as e:
        print("    [ERROR] Could not open image:", e)
        return ""

    try:
        text = pytesseract.image_to_string(img, lang="eng")
        if text.strip():
            print(f"    → Extracted {len(text)} characters from image")
        else:
            print("    [WARN] No text extracted from image")
        return text
    except Exception as e:
        print("    [ERROR] Tesseract OCR error:", e)
        return ""


# ---------- Parameter parsing from text
def parse_parameters_from_text(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns:
        {
           "hemoglobin": {
               "value_raw": "12.5",
               "unit_raw": "g/dL",
               "source_line": "...",
               ...
           },
           ...
        }
    """
    params: Dict[str, Dict[str, Any]] = {}

    lines = text.splitlines()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()

        # ---- Hemoglobin / Hb
        if "hemoglobin" in lower or "haemoglobin" in lower or " hb" in lower:
            m = re.search(
                r"(haemoglobin|hemoglobin|hb)[^0-9\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?",
                line,
                re.I,
            )
            if m and "hemoglobin" not in params:
                params["hemoglobin"] = {
                    "value_raw": m.group(2),
                    "unit_raw": m.group(3) or "",
                    "source_line": line,
                }
                continue

        # ---- RBC count
        if "rbc" in lower and "count" in lower:
            m = re.search(
                r"(rbc\s*count)[^0-9\-]*([0-9]+(?:\.[0-9]+)?)",
                line,
                re.I,
            )
            if m and "rbc_count" not in params:
                params["rbc_count"] = {
                    "value_raw": m.group(2),
                    "unit_raw": "",
                    "source_line": line,
                }
                continue

        # ---- Platelet count
        if "platelet" in lower and "count" in lower:
            m = re.search(
                r"(platelet\s*count)[^0-9\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/\.]+)?",
                line,
                re.I,
            )
            if m and "platelet_count" not in params:
                params["platelet_count"] = {
                    "value_raw": m.group(2),
                    "unit_raw": m.group(3) or "",
                    "source_line": line,
                }
                continue

        # ---- Glucose
        if "glucose" in lower or "blood sugar" in lower:
            m = re.search(
                r"(glucose|blood sugar)[^0-9\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/\.]+)?",
                line,
                re.I,
            )
            if m and "glucose" not in params:
                params["glucose"] = {
                    "value_raw": m.group(2),
                    "unit_raw": m.group(3) or "",
                    "source_line": line,
                }
                continue

        # ---- Cholesterol
        if "cholesterol" in lower:
            m = re.search(
                r"(cholesterol)[^0-9\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/\.]+)?",
                line,
                re.I,
            )
            if m and "cholesterol" not in params:
                params["cholesterol"] = {
                    "value_raw": m.group(2),
                    "unit_raw": m.group(3) or "",
                    "source_line": line,
                }
                continue

    # enrich with standard values + flags
    enriched: Dict[str, Dict[str, Any]] = {}
    for param, info in params.items():
        val_raw = info.get("value_raw")
        unit_raw = info.get("unit_raw", "")
        value_std, unit_std, note = convert_value_and_unit(param, val_raw, unit_raw)
        flag = interpret_param(param, value_std)

        enriched[param] = {
            "value_raw": val_raw,
            "unit_raw": unit_raw,
            "source_line": info.get("source_line", ""),
            "value_standard": value_std,
            "unit_standard": unit_std,
            "conversion_note": note,
            "flag": flag,
        }

    return enriched


# ---------- Processors for each type
def save_report_json(filename: str, payload: Dict[str, Any]) -> Path:
    out = ROW_REPORTS_DIR / filename
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print("    Saved parsed JSON to:", out.resolve())
    return out


def process_pdf_report(pdf_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    print(f"[{timestamp()}] PDF: {pdf_path.name}")
    text = extract_text_from_pdf(pdf_path)
    parsed_full = parse_parameters_from_text(text)

    # interpreted is just a shallow view with value + flag
    interpreted = {
        k: {
            "value_raw": v["value_raw"],
            "unit_raw": v["unit_raw"],
            "value_standard": v["value_standard"],
            "unit_standard": v["unit_standard"],
            "flag": v["flag"],
            "conversion_note": v["conversion_note"],
        }
        for k, v in parsed_full.items()
    }

    print(f"    Parsed from {pdf_path.name} :", parsed_full)
    print("    Interpreted:", interpreted)

    save_report_json(
        f"{pdf_path.stem}_week2_parsed.json",
        {
            "file": pdf_path.name,
            "type": "pdf",
            "parsed": parsed_full,
            "interpreted": interpreted,
        },
    )
    return parsed_full, interpreted


def process_image_report(image_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    print(f"[{timestamp()}] Image: {image_path.name}")
    text = ocr_image(image_path)
    parsed_full = parse_parameters_from_text(text)

    interpreted = {
        k: {
            "value_raw": v["value_raw"],
            "unit_raw": v["unit_raw"],
            "value_standard": v["value_standard"],
            "unit_standard": v["unit_standard"],
            "flag": v["flag"],
            "conversion_note": v["conversion_note"],
        }
        for k, v in parsed_full.items()
    }

    print(f"    Parsed from {image_path.name} :", parsed_full)
    print("    Interpreted:", interpreted)

    save_report_json(
        f"{image_path.stem}_week2_parsed.json",
        {
            "file": image_path.name,
            "type": "image",
            "parsed": parsed_full,
            "interpreted": interpreted,
        },
    )
    return parsed_full, interpreted


# ---------- Unified classifier
def classify_and_process_file(file_path: Path) -> Dict[str, Any]:
    ext = file_path.suffix.lower()
    summary: Dict[str, Any] = {
        "file": file_path.name,
        "ext": ext,
        "status": None,
        "parsed": {},
        "interpreted": {},
    }

    if ext in SUPPORTED_PDF_EXT:
        parsed, interpreted = process_pdf_report(file_path)
        summary["status"] = "ok_pdf"
        summary["parsed"] = parsed
        summary["interpreted"] = interpreted

    elif ext in SUPPORTED_IMAGE_EXT:
        parsed, interpreted = process_image_report(file_path)
        summary["status"] = "ok_image"
        summary["parsed"] = parsed
        summary["interpreted"] = interpreted

    elif ext in SUPPORTED_CSV_EXT:
        # For Week-2 we just acknowledge CSV and show basic info.
        print(f"[{timestamp()}] CSV: {file_path.name}")
        try:
            df = pd.read_csv(file_path)
            summary["status"] = "csv_dataset"
            summary["parsed"] = {
                "n_rows": len(df),
                "n_cols": len(df.columns),
                "columns": df.columns.tolist(),
            }
            print(
                f"    → CSV has {len(df)} rows and {len(df.columns)} columns. "
                "This dataset is handled more deeply in Week-1."
            )
        except Exception as e:
            print("    [WARN] Could not read CSV:", e)
            summary["status"] = "csv_error"

    else:
        print(
            f"[ERROR] Unsupported file: {file_path.name} "
            f"(extension {ext} not in supported medical document formats)"
        )
        summary["status"] = "unsupported"

    return summary


# ---------- MAIN
def main():
    print("Repo root:", REPO_ROOT)
    print("Week-2 reports dir:", REPORTS_DIR.resolve())

    if not REPORTS_DIR.exists():
        print("Reports folder not found at", REPORTS_DIR.resolve())
        return

    report_files = sorted(p for p in REPORTS_DIR.iterdir() if p.is_file())
    if not report_files:
        print("No report files found in", REPORTS_DIR.resolve())
        return

    print(f"Found {len(report_files)} file(s) in {REPORTS_DIR.relative_to(REPO_ROOT)}:")
    for f in report_files:
        print(" -", f.name)

    unsupported: list[str] = []
    all_summaries: list[Dict[str, Any]] = []

    for f in report_files:
        summary = classify_and_process_file(f)
        all_summaries.append(summary)
        if summary["status"] == "unsupported":
            unsupported.append(summary["file"])

    # Save unsupported log (and simple summary)
    unsupported_payload = {
        "generated_at": timestamp(),
        "unsupported_files": unsupported,
        "summary": all_summaries,
    }
    with open(UNSUPPORTED_LOG, "w", encoding="utf-8") as f:
        json.dump(unsupported_payload, f, indent=2, ensure_ascii=False)

    print("\nUnsupported files logged to:", UNSUPPORTED_LOG.resolve())


if __name__ == "__main__":
    main()
