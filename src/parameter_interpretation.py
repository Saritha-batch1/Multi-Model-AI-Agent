import pandas as pd
import os

# =============================
# Reference ranges (Model-1)
# =============================
REFERENCE_RANGES = {
    "hemoglobin": (12.0, 16.0),
    "wbc": (4000, 11000),
    "platelet": (150000, 450000),
    "glucose": (70, 140),
    "creatinine": (0.6, 1.3),
    "crp": (0, 5),
    "cholesterol": (0, 200)
}

STANDARD_UNITS = {
    "hemoglobin": "g/dl",
    "wbc": "cells/cumm",
    "platelet": "cells/cumm",
    "glucose": "mg/dl",
    "creatinine": "mg/dl",
    "crp": "mg/l",
    "cholesterol": "mg/dl"
}

def interpret_value(param, value):
    if param not in REFERENCE_RANGES:
        return "UNKNOWN"

    low, high = REFERENCE_RANGES[param]

    if value < low:
        return "LOW"
    elif value > high:
        return "HIGH"
    else:
        return "NORMAL"


def run_interpretation(input_path, output_path, source_name):
    df = pd.read_csv(input_path)

    # Drop rows with missing or non-numeric values
    df = df.dropna(subset=["parameter", "value"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    # Normalize parameter names
    df["parameter"] = df["parameter"].str.lower().str.strip()

    # Fill missing units
    if "unit" not in df.columns:
        df["unit"] = None

    df["unit"] = df.apply(
        lambda row: STANDARD_UNITS.get(row["parameter"], row["unit"])
        if pd.isna(row["unit"]) or str(row["unit"]).strip() == "" else row["unit"],
        axis=1
    )

    # Modify patient_id to row_id and ensure it starts from 0
    if "patient_id" in df.columns:
        df = df.rename(columns={"patient_id": "row_id"})
        df = df.reset_index(drop=True)
        df["row_id"] = df.index

    # Apply Model-1
    df["status"] = df.apply(
        lambda row: interpret_value(row["parameter"], row["value"]),
        axis=1
    )

    df["source"] = source_name

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\n✅ Model-1 Interpretation completed for {source_name}")
    print("Sample output:")
    print(df.head())


# =============================
# Run for OCR data
# =============================
run_interpretation(
    input_path="data/processed/ocr_blood_parameters.csv",
    output_path="data/processed/ocr_interpreted.csv",
    source_name="OCR"
)

# =============================
# Run for Healthcare data
# =============================
run_interpretation(
    input_path="data/processed/healthcare_blood_parameters.csv",
    output_path="data/processed/healthcare_interpreted.csv",
    source_name="HEALTHCARE"
)