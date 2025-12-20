import csv
import os

def validate_and_standardize(params: dict) -> dict:
    STANDARD_SCHEMA = {
        "hemoglobin": {"unit": "g/dl"},
        "wbc_count": {"unit": "/µl"},
        "platelet_count": {"unit": "/µl"},
        "glucose": {"unit": "mg/dl"},
        "tsh": {"unit": "µiu/ml"},
        "t3": {"unit": "ng/dl"},
        "t4": {"unit": "µg/dl"},
        "total_cholesterol": {"unit": "mg/dl"},
        "hdl_cholesterol": {"unit": "mg/dl"},
        "ldl_cholesterol": {"unit": "mg/dl"},
        "triglycerides": {"unit": "mg/dl"},
        "creatinine": {"unit": "mg/dl"},
        "urea": {"unit": "mg/dl"},
        "bilirubin_total": {"unit": "mg/dl"},
        "ast": {"unit": "u/l"},
        "alt": {"unit": "u/l"},
        "albumin": {"unit": "g/dl"},
        "calcium": {"unit": "mg/dl"},
        "sodium": {"unit": "mmol/l"},
        "potassium": {"unit": "mmol/l"},
        "esr": {"unit": "mm/hr"}
    }

    cleaned = {}

    for param, value in params.items():
        if param not in STANDARD_SCHEMA:
            continue

        try:
            value = float(value)
            status = "valid"
        except:
            cleaned[param] = {
                "value": None,
                "unit": STANDARD_SCHEMA[param]["unit"],
                "status": "invalid"
            }
            continue

        cleaned[param] = {
            "value": value,
            "unit": STANDARD_SCHEMA[param]["unit"],
            "status": status
        }

    return cleaned


# ---------------- SAVE OUTPUT ----------------
def save_validation_to_csv(patient_id: str, validated_data: dict):
    os.makedirs("outputs", exist_ok=True)
    file_path = "outputs/validated_parameters.csv"

    fieldnames = ["patient_id"]
    for param in validated_data.keys():
        fieldnames.extend([
            f"{param}_value",
            f"{param}_unit",
            f"{param}_status"
        ])

    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        row = {"patient_id": patient_id}
        for param, data in validated_data.items():
            row[f"{param}_value"] = data["value"]
            row[f"{param}_unit"] = data["unit"]
            row[f"{param}_status"] = data["status"]

        writer.writerow(row)
