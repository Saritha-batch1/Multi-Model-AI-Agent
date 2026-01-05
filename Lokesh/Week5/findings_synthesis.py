import json
import csv
import os
from collections import defaultdict


def load_csv_as_dict(path, key_field="patient_id"):
    data = defaultdict(dict)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row[key_field]
            data[pid].update(row)
    return data


def synthesize_findings(
    validated_csv,
    pattern_csv,
    risk_csv,
    output_path="outputs/week5/findings_summary.json"
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    validated = load_csv_as_dict(validated_csv)
    patterns = load_csv_as_dict(pattern_csv)
    risks = load_csv_as_dict(risk_csv)

    final_output = []

    for patient_id in validated.keys():
        abnormal = []
        key_findings = []
        reasons = {}

        # ---- Interpretation from validated data ----
        for param, value in validated[patient_id].items():
            if param.endswith("_status") and value in ["high", "low"]:
                clean_param = param.replace("_status", "")
                abnormal.append(clean_param)
                key_findings.append(
                    f"{clean_param.replace('_', ' ').title()} is {value}"
                )
                reasons[clean_param] = value

        # ---- Pattern insights ----
        pattern_notes = []
        for k, v in patterns.get(patient_id, {}).items():
            if v.lower() in ["high", "abnormal", "elevated"]:
                pattern_notes.append(k.replace("_", " ").title())

        # ---- Overall risk ----
        overall_risk = risks.get(patient_id, {}).get("risk_level", "unknown")

        confidence = (
            "high" if len(abnormal) >= 3 or overall_risk == "high"
            else "moderate" if abnormal
            else "low"
        )

        final_output.append({
            "patient_id": patient_id,
            "summary": {
                "key_findings": key_findings,
                "abnormal_parameters": abnormal,
                "identified_patterns": pattern_notes,
                "overall_risk": overall_risk,
                "confidence": confidence
            },
            "explainability": {
                "why_flagged": key_findings,
                "supporting_metrics": reasons
            }
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    print(f"Findings synthesis saved → {output_path}")
