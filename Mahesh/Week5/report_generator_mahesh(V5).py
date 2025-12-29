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

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

WEEK4_OUTPUT_PATH = ROOT_DIR / config["week4_output_path"]
WEEK5_OUTPUT_PATH = Path(__file__).parent / "output"
WEEK5_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def generate_recommendations(findings, overall_status):
    recs = []

    for item in findings:
        param = item.get("parameter")
        status = item.get("status")

        if param == "Glucose" and status in ["high", "moderate"]:
            recs.append(
                "Reduce sugar intake, exercise regularly, and monitor blood glucose levels."
            )

        if param == "Cholesterol" and status == "high":
            recs.append(
                "Adopt a low-fat diet, avoid fried foods, and include regular physical activity."
            )

        if param == "Hemoglobin" and status == "low":
            recs.append(
                "Include iron-rich foods such as leafy greens and legumes; consult a doctor if fatigue persists."
            )

    if overall_status in ["moderate-risk", "high-risk"]:
        recs.append(
            "Schedule a consultation with a healthcare professional for further evaluation."
        )

    if not recs:
        recs.append(
            "Maintain a balanced diet, regular exercise, and routine health checkups."
        )

    return list(set(recs))


def human_summary(user, overall_status, findings):
    lines = [
        f"This health report is generated for a {user.get('age')}-year-old {user.get('gender')} individual.",
        f"Overall health risk level is assessed as {overall_status.upper()}."
    ]

    for f in findings:
        lines.append(
            f"{f['parameter']} is {f['status']} ({f['meaning']})."
        )

    return " ".join(lines)

# ==================================================
# PROCESS WEEK-4 OUTPUT FILES
# ==================================================

week4_files = list(WEEK4_OUTPUT_PATH.glob("week4_final_summary_*.json"))

if not week4_files:
    raise FileNotFoundError("No Week-4 summary files found. Run Week-4 first.")

for file_path in week4_files:
    with open(file_path, "r", encoding="utf-8") as f:
        week4_data = json.load(f)

    user = week4_data.get("user_profile", {})
    findings = week4_data.get("health_findings", [])
    overall_status = week4_data.get("overall_health_status", "unknown")
    patterns = week4_data.get("patterns_detected", [])

    # ==================================================
    # SYNTHESIS
    # ==================================================

    summary_text = human_summary(user, overall_status, findings)
    recommendations = generate_recommendations(findings, overall_status)

    final_report = {
        "user_profile": user,
        "overall_health_status": overall_status,
        "summary": summary_text,
        "key_findings": findings,
        "patterns_identified": patterns,
        "recommendations": recommendations,
        "medical_disclaimer": (
            "This report is for informational purposes only and does not "
            "constitute medical advice or diagnosis. Please consult a qualified doctor."
        ),
        "generated_at": datetime.now().isoformat()
    }

    user_id = user.get("user_id", "unknown")
    output_file = WEEK5_OUTPUT_PATH / f"user_report_{user_id}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=4)

    print(f"[SUCCESS] Week-5 report generated: {output_file}")

print("\nWeek-5 synthesis and recommendation generation completed successfully.")

# ==================================================
# END
