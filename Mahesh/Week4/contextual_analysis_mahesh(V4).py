import json
from pathlib import Path
from datetime import datetime

# ==================================================
# CONFIG
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.json"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"config.json not found at {CONFIG_PATH}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

WEEK3_OUTPUT_PATH = ROOT_DIR / config["week3_output_path"]
WEEK4_OUTPUT_PATH = ROOT_DIR / config["week4_output_path"]
WEEK4_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# ==================================================
# LOAD WEEK-3 SUMMARY
# ==================================================

WEEK3_FILE = WEEK3_OUTPUT_PATH / "week3_summary.json"

if not WEEK3_FILE.exists():
    raise FileNotFoundError("Week-3 summary not found. Run Week-3 first.")

with open(WEEK3_FILE, "r", encoding="utf-8") as f:
    week3 = json.load(f)

# ==================================================
# USER CONTEXT (SIMULATED PROFILES)
# ==================================================

USER_PROFILES = [
    {"user_id": "TEST_MALE_45", "age": 45, "gender": "male"},
    {"user_id": "TEST_MALE_65", "age": 65, "gender": "male"},
    {"user_id": "TEST_FEMALE_28", "age": 28, "gender": "female"},
]

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def age_risk(age):
    return "elevated" if age >= 40 else "normal"

def hemoglobin_status(val, gender):
    if val is None:
        return None
    if gender == "female":
        return "low" if val < 12 else "normal"
    return "low" if val < 13 else "normal"

def glucose_status(val):
    if val is None:
        return None, None
    if val >= 126:
        return "high", "Diabetes risk"
    if val >= 100:
        return "moderate", "Prediabetes risk"
    return "normal", "Normal glucose"

def cholesterol_status(val):
    if val is None:
        return None, None
    if val >= 200:
        return "high", "Cardiovascular risk"
    return "normal", "Healthy level"

# ==================================================
# CONTEXTUAL ANALYSIS (MODEL-3)
# ==================================================

for user in USER_PROFILES:
    findings = []

    hb = week3.get("hb_median")
    if hb is not None:
        status = hemoglobin_status(hb, user["gender"])
        findings.append({
            "parameter": "Hemoglobin",
            "value": hb,
            "status": status,
            "meaning": "Possible anemia" if status == "low" else "Healthy level"
        })

    glucose = week3.get("glucose_median")
    if glucose is not None:
        status, msg = glucose_status(glucose)
        findings.append({
            "parameter": "Glucose",
            "value": glucose,
            "status": status,
            "meaning": msg
        })

    chol = week3.get("cholesterol_median")
    if chol is not None:
        status, msg = cholesterol_status(chol)
        findings.append({
            "parameter": "Cholesterol",
            "value": chol,
            "status": status,
            "meaning": msg
        })

    overall_status = "low-risk"
    if age_risk(user["age"]) == "elevated":
        overall_status = "moderate-risk"
    if any(f["status"] == "high" for f in findings):
        overall_status = "high-risk"

    final_output = {
        "user_profile": user,
        "overall_health_status": overall_status,
        "health_findings": findings,
        "patterns_detected": week3.get("computed_patterns", []),
        "medical_disclaimer": (
            "This report is generated for informational purposes only "
            "and must not be considered a medical diagnosis."
        ),
        "generated_at": datetime.now().isoformat()
    }

    out_file = WEEK4_OUTPUT_PATH / f"week4_final_summary_{user['user_id']}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    print(f"[SUCCESS] Week-4 report generated for {user['user_id']}")
