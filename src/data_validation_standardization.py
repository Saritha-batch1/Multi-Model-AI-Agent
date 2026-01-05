import pandas as pd
import os

# =========================
# Paths
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OCR_INPUT = os.path.join(BASE_DIR, "data", "processed", "ocr_blood_parameters.csv")
OCR_OUTPUT = os.path.join(BASE_DIR, "data", "processed", "ocr_validated_parameters.csv")

HC_INPUT = os.path.join(BASE_DIR, "data", "processed", "healthcare_blood_parameters.csv")
HC_OUTPUT = os.path.join(BASE_DIR, "data", "processed", "healthcare_validated_parameters.csv")

# =========================
# Standard units
# =========================
STANDARD_UNITS = {
    "crp": "mg/l",
    "hemoglobin": "g/dl",
    "wbc": "cells/cumm",
    "platelet": "cells/cumm",
    "glucose": "mg/dl",
    "creatinine": "mg/dl"
}

# =========================
# Unit conversion
# =========================
def convert_value(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value

    # mg/dl -> mg/l
    if from_unit == "mg/dl" and to_unit == "mg/l":
        return value * 10

    # mg/l -> mg/dl
    if from_unit == "mg/l" and to_unit == "mg/dl":
        return value / 10

    # g/l -> g/dl
    if from_unit == "g/l" and to_unit == "g/dl":
        return value / 10

    return value  # default (no conversion)

# =========================
# Validation rules
# =========================
def is_valid(param, value):
    if value is None or pd.isna(value):
        return False
    if value < 0:
        return False

    # basic physiological checks
    if param == "hemoglobin" and value > 25:
        return False
    if param == "wbc" and value > 200000:
        return False
    if param == "crp" and value > 500:
        return False

    return True

# =========================
# Process function
# =========================
def validate_and_standardize(input_path, output_path):
    df = pd.read_csv(input_path)

    clean_rows = []

    for _, row in df.iterrows():
        param = row["parameter"].lower()
        try:
            value = float(row["value"])
        except (ValueError, TypeError):
            continue
        unit = str(row["unit"]).lower() if pd.notna(row["unit"]) else ""

        if param not in STANDARD_UNITS:
            continue

        standard_unit = STANDARD_UNITS[param]
        value = convert_value(value, unit, standard_unit)

        if is_valid(param, value):
            row["value"] = round(value, 2)
            row["unit"] = standard_unit
            clean_rows.append(row)

    clean_df = pd.DataFrame(clean_rows)
    clean_df.to_csv(output_path, index=False)

    print(f"✅ Validated & standardized: {output_path}")
    print("Rows:", len(clean_df))
    print(clean_df.head())

# =========================
# Run for both datasets
# =========================
validate_and_standardize(OCR_INPUT, OCR_OUTPUT)
validate_and_standardize(HC_INPUT, HC_OUTPUT)