import csv
import os

# --------------------------------------------------
# Reference ranges (adult, general)
# --------------------------------------------------
REFERENCE_RANGES = {
    "hemoglobin": (13.0, 17.0),
    "wbc_count": (4000, 11000),
    "platelet_count": (150000, 450000),
    "glucose": (70, 110),
    "tsh": (0.4, 4.5),
    "t3": (80, 200),
    "t4": (5.0, 12.0),
    "total_cholesterol": (0, 200),
    "hdl_cholesterol": (40, 100),
    "ldl_cholesterol": (0, 100),
    "triglycerides": (0, 150),
    "creatinine": (0.6, 1.3),
    "urea": (15, 40),
    "bilirubin_total": (0.2, 1.2),
    "ast": (0, 40),
    "alt": (0, 40),
    "albumin": (3.5, 5.2),
    "calcium": (8.5, 10.5),
    "sodium": (135, 145),
    "potassium": (3.5, 5.1),
    "esr": (0, 20),
}

# --------------------------------------------------
# Model 1: Parameter Interpretation
# --------------------------------------------------
def interpret_parameters(validated_data: dict) -> dict:
    interpreted = {}

    for param, info in validated_data.items():
        value = info.get("value")

        if value is None or param not in REFERENCE_RANGES:
            interpreted[param] = {
                "value": value,
                "status": "unknown"
            }
            continue

        low, high = REFERENCE_RANGES[param]

        if value < low:
            status = "low"
        elif value > high:
            status = "high"
        else:
            status = "normal"

        interpreted[param] = {
            "value": value,
            "status": status
        }

    return interpreted

# --------------------------------------------------
# Save interpretation to CSV
# --------------------------------------------------
def save_interpretation_to_csv(patient_id: str, interpreted_data: dict):
    os.makedirs("outputs", exist_ok=True)
    file_path = "outputs/parameter_interpretation.csv"

    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["patient_id", "parameter", "value", "interpretation"])

        for param, info in interpreted_data.items():
            writer.writerow([
                patient_id,
                param,
                info.get("value"),
                info.get("status")
            ])
