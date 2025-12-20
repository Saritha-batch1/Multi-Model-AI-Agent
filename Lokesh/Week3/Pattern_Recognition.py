import csv
import os

def pattern_risk_assessment(validated_params: dict) -> dict:
    """
    Identifies risk patterns using combinations of parameters
    and produces basic risk scores.
    """

    def get(name):
        return validated_params.get(name, {}).get("value")

    risks = {
        "cardiovascular": 0,
        "metabolic": 0,
        "renal": 0,
        "liver": 0
    }

    # ---------------- Cardiovascular ----------------
    total_chol = get("total_cholesterol")
    hdl = get("hdl_cholesterol")
    ldl = get("ldl_cholesterol")
    triglycerides = get("triglycerides")

    if total_chol and total_chol > 240:
        risks["cardiovascular"] += 2
    if ldl and ldl > 160:
        risks["cardiovascular"] += 2
    if hdl and hdl < 40:
        risks["cardiovascular"] += 1
    if triglycerides and triglycerides > 200:
        risks["cardiovascular"] += 2

    if total_chol and hdl and hdl != 0:
        ratio = total_chol / hdl
        if ratio > 5:
            risks["cardiovascular"] += 2

    # ---------------- Metabolic (Diabetes) ----------------
    fasting_glucose = get("fasting_plasma_glucose")
    hba1c = get("hba1c")

    if fasting_glucose and fasting_glucose >= 126:
        risks["metabolic"] += 3
    elif fasting_glucose and fasting_glucose >= 100:
        risks["metabolic"] += 1

    if hba1c and hba1c >= 6.5:
        risks["metabolic"] += 3
    elif hba1c and hba1c >= 5.7:
        risks["metabolic"] += 1

    # ---------------- Renal ----------------
    creatinine = get("creatinine")
    urea = get("urea")

    if creatinine and creatinine > 1.3:
        risks["renal"] += 2
    if urea and urea > 40:
        risks["renal"] += 1

    # ---------------- Liver ----------------
    ast = get("ast")
    alt = get("alt")
    bilirubin = get("bilirubin_total")

    if ast and ast > 40:
        risks["liver"] += 1
    if alt and alt > 40:
        risks["liver"] += 1
    if bilirubin and bilirubin > 1.2:
        risks["liver"] += 1

    # ---------------- Risk Level Mapping ----------------
    result = {}
    for domain, score in risks.items():
        if score >= 4:
            level = "high"
        elif score >= 2:
            level = "moderate"
        else:
            level = "low"

        result[domain] = {
            "score": score,
            "level": level
        }

    return {
        "model": "pattern_recognition",
        "risks": result
    }


def save_pattern_risk_to_csv(patient_id: str, model2_output: dict, output_dir="outputs/model2"):
    """
    Saves Model 2 risk scores to CSV.
    Rows = patient_id
    Columns = risk domains
    """

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "pattern_risk_scores.csv")

    risks = model2_output["risks"]

    headers = ["patient_id"] + [f"{k}_score" for k in risks] + [f"{k}_level" for k in risks]

    row = [patient_id]
    for k in risks:
        row.append(risks[k]["score"])
    for k in risks:
        row.append(risks[k]["level"])

    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)
