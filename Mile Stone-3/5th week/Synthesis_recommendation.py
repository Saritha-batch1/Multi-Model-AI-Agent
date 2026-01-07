"""
##  Synthesis & Recommendation Generation (Model-4)

- Consumes Week-4 contextual outputs
- Generates human-friendly health summaries
- Produces actionable recommendations
- NO medical diagnosis
"""

import json
from pathlib import Path
from datetime import datetime

# ==================================================
# CONFIG (Week-5 local)
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

if not CONFIG_PATH.exists():
    raise FileNotFoundError("Week-5 config.json not found")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

WEEK4_INPUT_DIR = BASE_DIR / config["week4_output_path"]
WEEK5_OUTPUT_DIR = BASE_DIR / "output"
WEEK5_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# RECOMMENDATION LOGIC
# ==================================================

def generate_recommendations(findings, overall_status):
    recs = []

    for item in findings:
        param = item.get("parameter")
        status = item.get("status")

        if param == "Glucose" and status in {"high", "moderate"}:
            recs.append(
                "Reduce sugar intake, exercise regularly, and monitor blood glucose levels."
            )

        if param == "Cholesterol" and status == "high":
            recs.append(
                "Limit fatty foods, increase fiber intake, and engage in regular physical activity."
            )

        if param == "Hemoglobin" and status == "low":
            recs.append(
                "Include iron-rich foods such as leafy greens and legumes."
            )

    if overall_status in {"moderate-risk", "high-risk"}:
        recs.append(
            "Consider consulting a healthcare professional for further evaluation."
        )

    if not recs:
        recs.append(
            "Maintain a balanced diet, regular exercise, and routine health checkups."
        )

    return sorted(set(recs))

# ==================================================
# SUMMARY GENERATION
# ==================================================

def build_human_summary(user, overall_status, findings):
    age = user.get("age", "unknown")
    gender = user.get("gender", "unknown")

    lines = [
        f"This report is generated for a {age}-year-old {gender} individual.",
        f"Overall health risk level is assessed as {overall_status.upper()}."
    ]

    for f in findings:
        param = f.get("parameter")
        status = f.get("status")
        meaning = f.get("meaning", "No additional details available.")
        lines.append(f"{param} is {status} ({meaning}).")

    return " ".join(lines)

# ==================================================
# MAIN PIPELINE
# ==================================================

def main():
    print("Week-5 Synthesis & Recommendation started")

    if not WEEK4_INPUT_DIR.exists():
        raise FileNotFoundError("Week-4 output folder not found")

    week4_files = list(WEEK4_INPUT_DIR.glob("week4_final_summary_*.json"))
    if not week4_files:
        raise FileNotFoundError("No Week-4 summary files found")

    for file_path in week4_files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[SKIPPED] Invalid JSON: {file_path.name} → {e}")
            continue

        user = data.get("user_profile", {})
        findings = data.get("health_findings", [])
        overall_status = data.get("overall_health_status", "unknown")
        patterns = data.get("patterns_detected", [])

        summary_text = build_human_summary(user, overall_status, findings)
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
                "constitute medical advice or diagnosis. "
                "Please consult a qualified healthcare professional."
            ),
            "generated_at": datetime.now().isoformat()
        }

        user_id = user.get("user_id", file_path.stem)
        output_file = WEEK5_OUTPUT_DIR / f"user_report_{user_id}.json"
        output_file.write_text(json.dumps(final_report, indent=2), encoding="utf-8")

        print(f"[SUCCESS] Generated → {output_file.name}")

    print("✅ Week-5 synthesis completed successfully")

# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
