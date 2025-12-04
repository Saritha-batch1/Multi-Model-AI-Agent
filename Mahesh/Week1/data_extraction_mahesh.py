import pandas as pd
from pathlib import Path
import re
import pdfplumber
import pytesseract
import json
from datetime import datetime

REPO_ROOT = Path('.')                 
INPUT_CSV = REPO_ROOT / 'Mahesh' / 'Week1' / 'data' / 'healthcare_dataset.csv'
SAMPLE_PDFS_DIR = REPO_ROOT / 'Mahesh' / 'Week1' / 'data' / 'pdfs'

OUTPUT_DIR = REPO_ROOT / 'Mahesh' / 'Week1' / 'output'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DIR = OUTPUT_DIR / 'cleaned_versions'
CLEANED_DIR.mkdir(parents=True, exist_ok=True)
ROW_REPORTS_DIR = OUTPUT_DIR / 'row_reports'
ROW_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR = OUTPUT_DIR / 'metadata'
METADATA_DIR.mkdir(parents=True, exist_ok=True)

def now_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def normalize_col_name(col: str) -> str:
    col = str(col).strip().lower()
    col = re.sub(r'[\s/()\-]+', '_', col)
    col = re.sub(r'[^a-z0-9_]', '', col)
    return col

def try_float(x):
    try:
        if pd.isna(x):
            return None
        s = str(x).strip().replace(',', '')
        m = re.match(r'[-+]?\d+(\.\d+)?', s)
        return float(m.group(0)) if m else None
    except Exception:
        return None

# ---------- Versioned cleaned CSV writer
def save_versioned_cleaned_csv(df: pd.DataFrame):
    ts = now_timestamp()
    filename = f"cleaned_data_{ts}.csv"
    out = CLEANED_DIR / filename
    df.to_csv(out, index=False)
    #small metadata file capturing how many rows/cols and timestamp
    meta = {
        "filename": str(out.name),
        "rows": len(df),
        "cols": len(df.columns),
        "timestamp": ts
    }
    meta_out = METADATA_DIR / f"meta_{ts}.json"
    with open(meta_out, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    print("Saved versioned cleaned CSV to:", out.resolve())
    print("Saved metadata to:", meta_out.resolve())
    return out

def load_and_clean_csv(path: Path) -> pd.DataFrame:
    print("Loading CSV:", path.resolve())
    df = pd.read_csv(path)
    df.columns = [normalize_col_name(c) for c in df.columns]
    print("Columns found:", df.columns.tolist())
    df = df.dropna(how='all')
    str_cols = df.select_dtypes(include='object').columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
    for c in df.columns:
        if df[c].dtype == object:
            sample = df[c].dropna().astype(str).head(10)
            if not sample.empty and sample.str.match(r'^[-+]?\d+(\.\d+)?$').all():
                df[c] = pd.to_numeric(df[c], errors='coerce')
    return df
REFERENCE_RANGES = {
    'hemoglobin': {'male': (13.0, 17.0), 'female': (12.0, 15.5)},
    'glucose': {'any': (70, 99)},
    'cholesterol': {'any': (0, 200)},
    'rbc_count': {'male': (4.5, 5.5), 'female': (4.2, 5.4)},
    'platelet_count': {'any': (150000, 410000)},
}

def interpret_param(name: str, value, sex='any'):
    if value is None:
        return None
    key = str(name).lower()
    if 'hb' in key or 'hemoglobin' in key:
        param = 'hemoglobin'
    elif 'glucose' in key:
        param = 'glucose'
    elif 'chol' in key:
        param = 'cholesterol'
    elif 'rbc' in key and 'count' in key:
        param = 'rbc_count'
    elif 'platelet' in key:
        param = 'platelet_count'
    else:
        return None

    ranges = REFERENCE_RANGES.get(param)
    if not ranges:
        return None

    if sex and sex.lower() in ranges:
        low, high = ranges[sex.lower()]
    elif 'any' in ranges:
        low, high = ranges['any']
    else:
        low, high = list(ranges.values())[0]

    try:
        val = float(value)
    except Exception:
        return None

    if val < low:
        return 'low'
    if val > high:
        return 'high'
    return 'normal'
PLAUSIBLE_RANGES = {
    'glucose': (0.1, 1000),
    'hemoglobin': (0.1, 30),
    'cholesterol': (10, 1000),
    'platelet_count': (1000, 10000000),
    'rbc_count': (0.1, 50),
}

def plausible_value(param_key: str, v):
    if v is None:
        return False
    try:
        f = float(v)
    except:
        return False
    if 1900 <= f <= 2100: 
        return False
    if f < 0:
        return False
    for p, (lo, hi) in PLAUSIBLE_RANGES.items():
        if p in param_key:
            return (lo <= f <= hi)
    return 0 <= f <= 10000
# glucose: mmol/L -> mg/dL : multiply by 18
# cholesterol (total): mmol/L -> mg/dL : multiply by 38.67 (approx)
UNIT_MULTIPLIERS = {
    ('glucose', 'mmol'): 18.0,
    ('cholesterol', 'mmol'): 38.67,
}

def convert_unit_if_needed(param_key: str, value_str: str, context_line: str = None):
    v = try_float(value_str)
    if v is None:
        return None, None, False

    line = (context_line or "").lower()
    if 'mmol' in line:
        for (p, unit), mult in UNIT_MULTIPLIERS.items():
            if p in param_key:
                return round(v * mult, 2), 'mmol', True

    # heuristic: if glucose value is small (e.g., < 40) it's possibly mmol
    if 'glucose' in param_key and (0.5 <= v <= 35):
        if v < 40:
            return round(v * 18.0, 2), 'suspected_mmol', True

    if 'cholesterol' in param_key and (0.2 <= v <= 20):
        if v < 15:
            return round(v * 38.67, 2), 'suspected_mmol', True

    return v, None, False
def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if not page_text or page_text.strip() == "":
                    try:
                        img = page.to_image(resolution=200).original  
                        ocr_text = pytesseract.image_to_string(img)
                        if ocr_text and ocr_text.strip():
                            page_text = ocr_text
                    except Exception:
                        pass
                text += page_text + "\n"
    except Exception as e:
        print("pdfplumber error:", e)
    return text

def skip_line_filter(line: str) -> bool:
    if not line:
        return True
    s = line.strip()
    if re.match(r'^(p|pg|page)\s*\d+\b', s, re.I):
        return True
    if re.match(r'^[\d\W_]+$', s):
        return True
    if len(s) <= 2:
        return True
    if re.search(r'guideline|table of contents|references|appendix', s, re.I):
        return True
    return False

def parse_parameters_from_text(text: str):
    params = {}
    lines = text.splitlines()
    for line in lines:
        raw = line.strip()
        if skip_line_filter(raw):
            continue
        l = raw.lower()

        # hemoglobin
        m = re.search(r'\b(?:hemoglobin|hb)\b[^\d\-]{0,15}([0-9]+(?:\.[0-9]+)?)', raw, re.I)
        if m:
            val_raw = m.group(1)
            val_conv, unit, converted = convert_unit_if_needed('hemoglobin', val_raw, raw)
            if plausible_value('hemoglobin', val_conv):
                params['hemoglobin'] = {'value_raw': val_raw, 'value': val_conv, 'unit': unit, 'converted': converted}
                continue

        # glucose
        m = re.search(r'\bglucose\b[^\d\-]{0,15}([0-9]+(?:\.[0-9]+)?)', raw, re.I)
        if m:
            val_raw = m.group(1)
            val_conv, unit, converted = convert_unit_if_needed('glucose', val_raw, raw)
            if plausible_value('glucose', val_conv):
                params['glucose'] = {'value_raw': val_raw, 'value': val_conv, 'unit': unit, 'converted': converted}
                continue

        # cholesterol
        m = re.search(r'\b(?:cholesterol|total cholesterol|t\.chol)\b[^\d\-]{0,15}([0-9]+(?:\.[0-9]+)?)', raw, re.I)
        if m:
            val_raw = m.group(1)
            val_conv, unit, converted = convert_unit_if_needed('cholesterol', val_raw, raw)
            if plausible_value('cholesterol', val_conv):
                params['cholesterol'] = {'value_raw': val_raw, 'value': val_conv, 'unit': unit, 'converted': converted}
                continue

        # platelets
        m = re.search(r'\bplatelet(?:s|_count)?\b[^\d\-]{0,15}([0-9]{4,8})', raw, re.I)
        if m:
            val_raw = m.group(1)
            val_conv, unit, converted = convert_unit_if_needed('platelet_count', val_raw, raw)
            if plausible_value('platelet_count', val_conv):
                params['platelet_count'] = {'value_raw': val_raw, 'value': val_conv, 'unit': unit, 'converted': converted}
                continue

    simplified = {}
    for k, v in params.items():
        simplified[k] = v['value']
    return simplified, params  

def demo_pdf_parse(pdf_path: Path):
    text = extract_text_from_pdf(pdf_path)
    parsed_simple, parsed_detailed = parse_parameters_from_text(text)
    print("Parsed from", pdf_path.name, ":", parsed_simple)
    interpreted = {}
    for k, v in parsed_simple.items():
        interp = interpret_param(k, v)
        interpreted[k] = {'value': v, 'flag': interp}
    print("Interpreted:", interpreted)
    out = ROW_REPORTS_DIR / f"{pdf_path.stem}_parsed.json"
    report = {
        'file': pdf_path.name,
        'parsed_simple': parsed_simple,
        'parsed_detailed': parsed_detailed,
        'interpreted': interpreted,
        'timestamp': now_timestamp()
    }
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print("Saved parsed JSON to:", out.resolve())
    return parsed_simple, parsed_detailed, interpreted
RANGE_PATTERNS = [
    # matches patterns like "Hemoglobin: 13.0 - 17.0 g/dL" or "Hemoglobin (g/dL) 13.0–17.0"
    re.compile(r'(hemoglobin|hb)[^0-9]{0,30}([0-9]+(?:\.[0-9]+)?)\s*[–\-]\s*([0-9]+(?:\.[0-9]+)?)', re.I),
    re.compile(r'(glucose)[^0-9]{0,30}([0-9]+(?:\.[0-9]+)?)\s*[–\-]\s*([0-9]+(?:\.[0-9]+)?)', re.I),
    re.compile(r'(cholesterol)[^0-9]{0,30}([0-9]+(?:\.[0-9]+)?)\s*[–\-]\s*([0-9]+(?:\.[0-9]+)?)', re.I),
]

def extract_ranges_from_guidelines(pdf_dir: Path):
    updated = {}
    if not pdf_dir.exists():
        return updated
    for p in pdf_dir.glob('*.pdf'):
        try:
            with pdfplumber.open(str(p)) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages)
            for pat in RANGE_PATTERNS:
                for m in pat.finditer(text):
                    key = m.group(1).lower()
                    low = float(m.group(2))
                    high = float(m.group(3))
                    if 'hb' in key or 'hemoglobin' in key:
                        canonical = 'hemoglobin'
                    elif 'glucose' in key:
                        canonical = 'glucose'
                    elif 'chol' in key:
                        canonical = 'cholesterol'
                    else:
                        canonical = key
                    if 0 < low < high < 10000:
                        updated[canonical] = (low, high)
        except Exception:
            continue
    for k, (lo, hi) in updated.items():
        if k in REFERENCE_RANGES:
            REFERENCE_RANGES[k]['any'] = (lo, hi)
        else:
            REFERENCE_RANGES[k] = {'any': (lo, hi)}
    if updated:
        print("Auto-updated REFERENCE_RANGES from guideline PDFs for:", list(updated.keys()))
    return updated

if __name__ == '__main__':
    extract_ranges_from_guidelines(SAMPLE_PDFS_DIR)
    if INPUT_CSV.exists():
        df = load_and_clean_csv(INPUT_CSV)
        saved_path = save_versioned_cleaned_csv(df)  
        print("Preview rows:\n", df.head().to_string(index=False))
    else:
        print("Input CSV not found at", INPUT_CSV.resolve())
        print("Please move healthcare_dataset.csv to Mahesh/Week1/data/ or update INPUT_CSV in the script.")
    if SAMPLE_PDFS_DIR.exists():
        pdfs = list(SAMPLE_PDFS_DIR.glob('*.pdf'))
        if not pdfs:
            print("No PDF files found in", SAMPLE_PDFS_DIR.resolve())
        else:
            for p in pdfs:
                demo_pdf_parse(p)
    else:
        print("No sample PDF folder found at", SAMPLE_PDFS_DIR.resolve(),
              "- create it and add sample PDFs to test parsing.")
