import csv
import os
def assess_overall_risk(interpreted_params: dict, model2_output: dict) -> dict:
    """
    Produces final patient-level risk assessment
    """

    abnormal_count = 0
    critical_flags = []

    # -------- Count abnormal parameters --------
    for param, data in interpreted_params.items():
        if data.get("interpretation") in ["high", "low"]:
            abnormal_count += 1

    # -------- Analyze Model 2 risks --------
    domain_risks = model2_output["risks"]

    high_risk_domains = [
        domain for domain, d in domain_risks.items()
        if d["level"] == "high"
    ]

    moderate_risk_domains = [
        domain for domain, d in domain_risks.items()
        if d["level"] == "moderate"
    ]

    # -------- Medical flags --------
    if domain_risks["cardiovascular"]["score"] >= 5:
        critical_flags.append("high cardiovascular risk")

    if domain_risks["metabolic"]["score"] >= 4:
        critical_flags.append("diabetes risk")

    if domain_risks["renal"]["score"] >= 3:
        critical_flags.append("renal function risk")

    if domain_risks["liver"]["score"] >= 3:
        critical_flags.append("liver function risk")

    # -------- Overall risk decision --------
    if len(high_risk_domains) >= 2 or abnormal_count >= 8:
        overall = "high"
    elif len(high_risk_domains) == 1 or abnormal_count >= 4:
        overall = "moderate"
    else:
        overall = "low"

    return {
        "overall_risk": overall,
        "abnormal_parameters": abnormal_count,
        "high_risk_domains": high_risk_domains,
        "moderate_risk_domains": moderate_risk_domains,
        "flags": critical_flags
    }




def save_risk_assessment_to_csv(patient_id: str, risk_result: dict, output_dir="outputs/model4"):
    """
    Saves final risk assessment to CSV.
    One row per patient.
    """

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "final_risk_assessment.csv")

    headers = [
        "patient_id",
        "overall_risk",
        "abnormal_parameters",
        "high_risk_domains",
        "moderate_risk_domains",
        "flags"
    ]

    row = [
        patient_id,
        risk_result.get("overall_risk"),
        risk_result.get("abnormal_parameters"),
        ",".join(risk_result.get("high_risk_domains", [])),
        ",".join(risk_result.get("moderate_risk_domains", [])),
        ",".join(risk_result.get("flags", []))
    ]

    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)
