import json
from pathlib import Path
from datetime import datetime

# ==================================================
# LOAD CONFIGURATION
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.json"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"config.json not found at {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

WEEK4_OUTPUT_PATH = ROOT_DIR / config["week4_output_path"]
WEEK5_OUTPUT_PATH = Path(__file__).parent / "output"
WEEK5_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def generate_recommendations(findings, overall_status):
    """
    Generate actionable recommendations linked to findings
    """
    recs = []

    for item in findings:
        param = item.get("parameter")
        status = item.get("status")

        if param == "Glucose" and status in ["high", "moderate"]:
            recs.append({
                "action": "Monitor blood glucose and reduce sugar intake",
                "reason": "Elevated glucose levels detected"
            })

        if param == "Cholesterol" and status == "high":
            recs.append({
                "action": "Adopt a low-fat diet and regular physical activity",
                "reason": "High cholesterol may increase cardiovascular risk"
            })

        if param == "Hemoglobin" and status == "low":
            recs.append({
                "action": "Increase iron-rich foods and consult a doctor if fatigue continues",
                "reason": "Low hemoglobin may indicate anemia"
            })

    if overall_status in ["moderate-risk", "high-risk"]:
        recs.append({
            "action": "Consult a healthcare professional",
            "reason": "Overall health risk requires further evaluation"
        })

    if not recs:
        recs.append({
            "action": "Maintain healthy lifestyle habits",
            "reason": "All parameters are within normal range"
        })

    return recs


def generate_human_summary(user, overall_status, findings):
    """
    Generate human-readable summary
    """
    lines = [
        f"This health report is generated for a {user['age']}-year-old {user['gender']} individual.",
        f"Overall health risk level is assessed as **{overall_status.upper()}**."
    ]

    for f in findings:
        lines.append(
            f"{f['parameter']} is {f['status']} — {f['meaning']}."
        )

    return " ".join(lines)

# ==================================================
# PROCESS WEEK-4 OUTPUT FILES
# ==================================================

week4_files = list(WEEK4_OUTPUT_PATH.glob("week4_final_summary_*.json"))

if not week4_files:
    raise FileNotFoundError("No Week-4 summary files found. Run Week-4 first.")

for file_path in week4_files:
    with open(file_path, "r") as f:
        week4_data = json.load(f)

    user = week4_data.get("user_profile", {})
    findings = week4_data.get("health_findings", [])
    overall_status = week4_data.get("overall_health_status", "unknown")
    patterns = week4_data.get("patterns_detected", [])

    # ==================================================
    # SYNTHESIS (MODEL-4 OUTPUT)
    # ==================================================

    summary_text = generate_human_summary(user, overall_status, findings)
    recommendations = generate_recommendations(findings, overall_status)

    final_report = {
        "user_profile": user,
        "overall_health_status": overall_status,
        "summary": summary_text,
        "key_findings": findings,
        "patterns_identified": patterns,
        "recommendations": recommendations,
        "severity_level": overall_status,
        "confidence": "rule-based analysis",
        "medical_disclaimer": (
            "This report is generated for informational purposes only. "
            "It does not constitute medical advice or diagnosis. "
            "Please consult a qualified healthcare professional."
        ),
        "generated_at": datetime.now().isoformat()
    }

    # ==================================================
    # SAVE WEEK-5 REPORT
    # ==================================================

    user_id = user.get("user_id", "unknown")
    output_file = WEEK5_OUTPUT_PATH / f"user_report_{user_id}.json"

    with open(output_file, "w") as f:
        json.dump(final_report, f, indent=4)

    print(f"[SUCCESS] Week-5 report generated: {output_file}")

print("\n✅ Week-5 synthesis & recommendation generation completed.")
