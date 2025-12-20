import csv
import os


# --------------------------------------------------
# Reference ranges (same schema as validation)
# --------------------------------------------------
REFERENCE_RANGES = {
    "hemoglobin": (12.0, 18.0),
    "wbc_count": (4000, 11000),
    "platelet_count": (120000, 380000),
    "glucose": (70, 140),
    "tsh": (0.38, 5.33),
    "t3": (87, 178),
    "t4": (4.82, 15.65),
    "total_cholesterol": (0, 200),
    "hdl_cholesterol": (40, 60),
    "ldl_cholesterol": (0, 130),
    "triglycerides": (0, 150),
    "creatinine": (0.7, 1.2),
    "urea": (21, 40),
    "bilirubin_total": (0.2, 1.2),
    "ast": (0, 40),
    "alt": (0, 41),
    "albumin": (3.5, 5.0),
    "calcium": (8.5, 10.5),
    "sodium": (136, 145),
    "potassium": (3.3, 5.1),
    "esr": (0, 15)
}


# --------------------------------------------------
# Task 4: Interpret parameters
# --------------------------------------------------
def interpret_parameters(validated_data: dict) -> dict:
    interpreted = {}

    for param, data in validated_data.items():
        value = data.get("value")

        if value is None or param not in REFERENCE_RANGES:
            interpreted[param] = {
                "value": value,
                "unit": data.get("unit"),
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
            "unit": data.get("unit"),
            "status": status
        }

    return interpreted


# --------------------------------------------------
# Save interpretation to CSV
# --------------------------------------------------
def save_interpretation_to_csv(patient_id: str, interpreted_data: dict):
    os.makedirs("outputs/interpreted", exist_ok=True)

    file_path = "outputs/interpreted/parameter_interpretation.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "patient_id",
                "parameter",
                "value",
                "unit",
                "status"
            ])

        for param, data in interpreted_data.items():
            writer.writerow([
                patient_id,
                param,
                data["value"],
                data["unit"],
                data["status"]
            ])
