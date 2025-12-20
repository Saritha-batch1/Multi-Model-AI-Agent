import re
import csv
import os

# -------------------------------------------------
# Fixed known parameters (LOCKED)
# -------------------------------------------------
KNOWN_PARAMETERS = {
    "patient_name",
    "age",
    "gender",

    "fasting_plasma_glucose",
    "post_prandial_plasma_glucose",
    "hba1c",

    "total_cholesterol",
    "hdl_cholesterol",
    "ldl_cholesterol",
    "triglycerides",

    "tsh",
    "t3",
    "t4",

    "bilirubin_total",
    "sgot",
    "sgpt",
    "alp",

    "urea",
    "creatinine",

    "hemoglobin",
    "wbc_count",
    "platelet_count"
}

# -------------------------------------------------
# Normalize parameter labels found in text
# -------------------------------------------------
PARAMETER_ALIASES = {
    "hemoglobin": ["hemoglobin", "haemoglobin"],
    "wbc_count": ["wbc", "total leukocyte count"],
    "platelet_count": ["platelet"],
    "fasting_plasma_glucose": ["fasting plasma glucose", "fpg"],
    "post_prandial_plasma_glucose": ["post prandial plasma glucose", "ppg"],
    "hba1c": ["hba1c"],
    "total_cholesterol": ["total cholesterol"],
    "hdl_cholesterol": ["hdl cholesterol"],
    "ldl_cholesterol": ["ldl cholesterol"],
    "triglycerides": ["triglycerides"],
    "tsh": ["tsh"],
    "t3": ["t3"],
    "t4": ["t4"],
    "bilirubin_total": ["bilirubin total"],
    "sgot": ["sgot", "ast"],
    "sgpt": ["sgpt", "alt"],
    "alp": ["alkaline phosphatase", "alp"],
    "urea": ["urea"],
    "creatinine": ["creatinine"],
}

# -------------------------------------------------
# Extract parameters from text
# -------------------------------------------------
def extract_parameters(text: str) -> dict:
    extracted = {p: None for p in KNOWN_PARAMETERS}

    lines = text.lower().splitlines()

    for line in lines:
        for param, aliases in PARAMETER_ALIASES.items():
            if param not in extracted:
                continue

            if any(alias in line for alias in aliases):
                match = re.search(r"([-+]?\d*\.?\d+)", line)
                if match:
                    extracted[param] = float(match.group())

    # Extract patient info separately
    name_match = re.search(r"patient name\s*[:\-]\s*([a-z\s]+)", text, re.I)
    if name_match:
        extracted["patient_name"] = name_match.group(1).strip()

    age_match = re.search(r"age\s*[:\-]\s*(\d+)", text, re.I)
    if age_match:
        extracted["age"] = float(age_match.group(1))

    gender_match = re.search(r"(male|female)", text, re.I)
    if gender_match:
        extracted["gender"] = gender_match.group(1).lower()

    return extracted

# -------------------------------------------------
# Save extracted parameters to CSV
# -------------------------------------------------
def save_to_csv(patient_id: str, parameters: dict):
    os.makedirs("outputs", exist_ok=True)
    file_path = "outputs/task2_parameters.csv"

    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["patient_id"] + list(KNOWN_PARAMETERS)
        )

        if not file_exists:
            writer.writeheader()

        row = {"patient_id": patient_id}
        row.update(parameters)
        writer.writerow(row)
