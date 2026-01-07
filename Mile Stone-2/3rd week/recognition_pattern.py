"""
   ## Pattern Recognition & Basic Risk Scoring (Model-2)

✔ Consumes Week-2 parsed JSON files
✔ Performs rule-based medical pattern recognition
✔ Generates per-report analysis JSONs
✔ Generates week3_summary.json for Week-4
✔ Safe, explainable, non-diagnostic

Author: Praveen
"""

import json
import statistics
from pathlib import Path
from datetime import datetime

# ==================================================
# PATH CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "data" / "week2_json_reports"
OUTPUT_DIR = BASE_DIR / "output" / "week3_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# SAFE HELPERS
# ==================================================

def safe_float(x):
    try:
        return float(str(x).strip())
    except Exception:
        return None

def extract_param(params, key):
    if not isinstance(params, dict):
        return None
    if key in params:
        v = params[key]
        if isinstance(v, dict):
            return v.get("value_standard")
        return v
    return None

# ==================================================
# PARAMETER EVALUATION
# ==================================================

def hemoglobin_status(v):
    v = safe_float(v)
    if v is None: return None
    if v < 8: return "severe"
    if v < 11: return "moderate"
    if v < 13: return "mild"
    return "normal"

def glucose_status(v):
    v = safe_float(v)
    if v is None: return None
    if v < 100: return "normal"
    if v < 126: return "prediabetes"
    return "diabetes-risk"

def cholesterol_status(v):
    v = safe_float(v)
    if v is None: return None
    if v < 200: return "normal"
    if v < 240: return "borderline"
    return "high"

def platelet_status(v):
    v = safe_float(v)
    if v is None: return None
    if v < 150000: return "low"
    if v > 450000: return "high"
    return "normal"

def rbc_status(v):
    v = safe_float(v)
    if v is None: return None
    if v < 4.2: return "low"
    if v > 5.9: return "high"
    return "normal"

# ==================================================
# PATTERN DETECTION
# ==================================================

def detect_patterns(hb, rbc, glucose, cholesterol, platelets):
    patterns = []

    if hb in ["mild", "moderate", "severe"] and rbc == "low":
        patterns.append("Anemia pattern detected")

    if glucose in ["prediabetes", "diabetes-risk"] and cholesterol in ["borderline", "high"]:
        patterns.append("Metabolic syndrome indicators present")

    if platelets == "low":
        patterns.append("Possible bleeding tendency")

    if not patterns:
        patterns.append("Healthy profile detected")

    return patterns

# ==================================================
# WEEK-3 SUMMARY GENERATION (IMPORTANT FIX)
# ==================================================

def generate_week3_summary():
    hb_vals, glucose_vals, cholesterol_vals = [], [], []
    all_patterns = []

    for file in OUTPUT_DIR.iterdir():
        if not file.name.endswith("_week3_analysis.json"):
            continue

        data = json.loads(file.read_text(encoding="utf-8"))

        for f in data.get("health_findings", []):
            val = f.get("value")

            if isinstance(val, (int, float)):
                if f["parameter"] == "Hemoglobin":
                    hb_vals.append(val)
                elif f["parameter"] == "Glucose":
                    glucose_vals.append(val)
                elif f["parameter"] == "Cholesterol":
                    cholesterol_vals.append(val)

        all_patterns.extend(data.get("patterns", []))

    summary = {
        "generated_at": datetime.now().isoformat(),
        "reports_count": len(list(OUTPUT_DIR.glob("*_week3_analysis.json"))),
        "hb_median": statistics.median(hb_vals) if hb_vals else None,
        "glucose_median": statistics.median(glucose_vals) if glucose_vals else None,
        "cholesterol_median": statistics.median(cholesterol_vals) if cholesterol_vals else None,
        "computed_patterns": list(set(all_patterns))
    }

    out_file = OUTPUT_DIR / "week3_summary.json"
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[SUCCESS] Week-3 summary generated → {out_file.name}")


# ==================================================
# MAIN PROCESS
# ==================================================

def main():
    print("Week-3 Pattern Recognition started")

    if not INPUT_DIR.exists():
        print("❌ Week-2 input folder not found:", INPUT_DIR)
        return

    for file in INPUT_DIR.iterdir():
        if file.suffix != ".json":
            continue

        data = json.loads(file.read_text(encoding="utf-8"))
        parsed = data.get("parsed", data)
        params = parsed.get("parameters", {})

        hb_val = extract_param(params, "hemoglobin")
        rbc_val = extract_param(params, "rbc_count")
        glucose_val = extract_param(params, "glucose")
        cholesterol_val = extract_param(params, "cholesterol")
        platelets_val = extract_param(params, "platelet_count")

        hb = hemoglobin_status(hb_val)
        rbc = rbc_status(rbc_val)
        glucose = glucose_status(glucose_val)
        cholesterol = cholesterol_status(cholesterol_val)
        platelets = platelet_status(platelets_val)

        patterns = detect_patterns(hb, rbc, glucose, cholesterol, platelets)

        analysis = {
            "health_findings": [
                {"parameter": "Hemoglobin", "value": hb_val, "status": hb},
                {"parameter": "RBC", "value": rbc_val, "status": rbc},
                {"parameter": "Glucose", "value": glucose_val, "status": glucose},
                {"parameter": "Cholesterol", "value": cholesterol_val, "status": cholesterol},
                {"parameter": "Platelets", "value": platelets_val, "status": platelets}
            ],
            "patterns": patterns,
            "notes": "This is not a medical diagnosis."
        }

        out_file = OUTPUT_DIR / file.name.replace("_week2_parsed", "_week3_analysis")
        out_file.write_text(json.dumps(analysis, indent=2), encoding="utf-8")

        print(f"[PROCESSED] {file.name} → {out_file.name}")

    # 🔑 THIS IS THE FIX
    generate_week3_summary()

    print("✅ Week-3 processing completed")

# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
