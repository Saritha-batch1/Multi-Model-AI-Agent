import json
from pathlib import Path
from datetime import datetime

# ==================================================
# CONFIGURATION (FIXED ROOT PATH)
# ==================================================

# Project root: Infosys Internship
ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.json"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"config.json not found at {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

WEEK3_OUTPUT_PATH = ROOT_DIR / config["week3_output_path"]
WEEK4_OUTPUT_PATH = ROOT_DIR / config["week4_output_path"]

# ==================================================
# USER PROFILES (SIMULATES LOGIN)
# ==================================================

USERS_DIR = Path(__file__).parent / "data" 

# 👉 Change only this line to test another user
ACTIVE_USER_FILE = "user_male_100.json"
USER_PROFILE_PATH = USERS_DIR / ACTIVE_USER_FILE

if not USER_PROFILE_PATH.exists():
    raise FileNotFoundError(f"User profile not found: {USER_PROFILE_PATH}")

with open(USER_PROFILE_PATH, "r") as f:
    user = json.load(f)

user_id = user.get("user_id", ACTIVE_USER_FILE.replace(".json", ""))
age = user["age"]
gender = user["gender"].lower()

# ==================================================
# HELPER FUNCTIONS (MODEL-3 CONTEXT LOGIC)
# ==================================================

def hemoglobin_status(hb):
    if gender == "female":
        return "low" if hb < 12 else "normal"
    return "low" if hb < 13 else "normal"

def glucose_status(val):
    if val >= 126:
        return "high", "High diabetes risk"
    elif val >= 100:
        return "moderate", "Prediabetes risk"
    return "normal", "Normal glucose level"

def cholesterol_status(val):
    if val >= 200:
        return "high", "Increased heart disease risk"
    return "normal", "Healthy cholesterol level"

def age_risk():
    return "elevated" if age >= 40 else "normal"

# ==================================================
# LOAD WEEK-3 SUMMARY (MODEL-2 OUTPUT)
# ==================================================

WEEK3_SUMMARY_FILE = WEEK3_OUTPUT_PATH / "week3_summary.json"

if not WEEK3_SUMMARY_FILE.exists():
    raise FileNotFoundError("Week-3 summary not found. Run Week-3 first.")

with open(WEEK3_SUMMARY_FILE, "r") as f:
    week3 = json.load(f)

parameters = week3.get("parameters", {})
patterns = week3.get("patterns_detected", [])

# ==================================================
# CONTEXTUAL ANALYSIS (MODEL-3)
# ==================================================

findings = []

# Hemoglobin
if "hemoglobin" in parameters:
    hb = parameters["hemoglobin"]["value_standard"]
    status = hemoglobin_status(hb)
    findings.append({
        "parameter": "Hemoglobin",
        "value": hb,
        "status": status,
        "meaning": "Possible anemia" if status == "low" else "Healthy level"
    })

# Glucose
if "glucose" in parameters:
    g = parameters["glucose"]["value_standard"]
    status, msg = glucose_status(g)
    findings.append({
        "parameter": "Glucose",
        "value": g,
        "status": status,
        "meaning": msg
    })

# Cholesterol
if "cholesterol" in parameters:
    c = parameters["cholesterol"]["value_standard"]
    status, msg = cholesterol_status(c)
    findings.append({
        "parameter": "Cholesterol",
        "value": c,
        "status": status,
        "meaning": msg
    })

# ==================================================
# OVERALL HEALTH STATUS
# ==================================================

overall_status = "low-risk"

if age_risk() == "elevated":
    overall_status = "moderate-risk"

if any(f["status"] == "high" for f in findings):
    overall_status = "high-risk"

# ==================================================
# FINAL OUTPUT (USER-FRIENDLY)
# ==================================================

final_output = {
    "user_profile": {
        "user_id": user_id,
        "age": age,
        "gender": gender
    },
    "overall_health_status": overall_status,
    "patterns_detected": patterns,
    "health_findings": findings,
    "recommendations": [
        "Consult a qualified doctor for confirmation",
        "Maintain a balanced diet and regular exercise",
        "Schedule periodic health checkups"
    ],
    "medical_disclaimer": (
        "This report is generated for informational purposes only "
        "and must not be considered a medical diagnosis."
    ),
    "generated_at": datetime.now().isoformat()
}

# ==================================================
# SAVE OUTPUT
# ==================================================

WEEK4_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
output_file = WEEK4_OUTPUT_PATH / f"week4_final_summary_{user_id}.json"

with open(output_file, "w") as f:
    json.dump(final_output, f, indent=4)

print(f"[SUCCESS] Week-4 analysis completed for user: {user_id}")
print(f"[OUTPUT] Saved at: {output_file}")
