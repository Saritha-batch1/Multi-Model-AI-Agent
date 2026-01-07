## load dataset
## clean data
## column normalization
## simple rules for classification

import pandas as pd
import numpy as np
import os
from pathlib import Path

# -----------------------------
# Step 1: Load dataset (PIPELINE-SAFE)
# -----------------------------
BASE_DIR = Path(__file__).parent
input_path = BASE_DIR / "Data" / "CSVs" / "complete_blood_count.csv"

if not input_path.exists():
    raise FileNotFoundError(f"Input CSV not found: {input_path}")

df = pd.read_csv(input_path)

print("Original columns:")
print(df.columns.tolist())

# -------------------------------------
# Step 2: Normalize column names
# -------------------------------------
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
)

print("\nNormalized columns:")
print(df.columns.tolist())

# -------------------------------------
# Step 3: Define key medical columns
# -------------------------------------
key_columns = [
    "age",
    "gender",
    "hemoglobin",
    "red_blood_cells",
    "white_blood_cells",
    "platelet_count",
    "glucose",
    "cholesterol_total"
]

# Keep only columns that exist in dataset
key_columns = [col for col in key_columns if col in df.columns]

# -------------------------------------
# Step 4: Drop rows where ALL key values are missing
# -------------------------------------
df = df.dropna(subset=key_columns, how="all")

print(f"\nRows after dropping fully empty medical records: {len(df)}")

# -------------------------------------
# Step 5: Handle NaNs for critical columns
# -------------------------------------
critical_columns = ["glucose", "hemoglobin", "cholesterol_total"]
critical_columns = [c for c in critical_columns if c in df.columns]

for col in critical_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------------------
# Step 6: Rule-based classification
# -------------------------------------

# ---- Glucose Status ----
def classify_glucose(value):
    if pd.isna(value):
        return "Unknown"
    if value < 70:
        return "Low"
    elif 70 <= value <= 99:
        return "Normal"
    elif 100 <= value <= 125:
        return "High"
    elif value >= 126:
        return "Very High"
    return "Unknown"

df["glucose_status"] = df["glucose"].apply(classify_glucose)

# ---- Hemoglobin Status ----
def classify_hemoglobin(row):
    value = row.get("hemoglobin")
    gender = row.get("gender")

    if pd.isna(value) or pd.isna(gender):
        return "Unknown"

    gender = str(gender).lower()

    if gender == "male":
        if value < 13:
            return "Low"
        elif 13 <= value <= 17:
            return "Normal"
        else:
            return "High"

    elif gender == "female":
        if value < 12:
            return "Low"
        elif 12 <= value <= 15.5:
            return "Normal"
        else:
            return "High"

    return "Unknown"

df["hemoglobin_status"] = df.apply(classify_hemoglobin, axis=1)

# ---- Cholesterol Status ----
if "cholesterol_total" in df.columns:
    def classify_cholesterol(value):
        if pd.isna(value):
            return "Unknown"
        if value < 200:
            return "Normal"
        elif 200 <= value <= 239:
            return "Borderline"
        else:
            return "High"

    df["cholesterol_status"] = df["cholesterol_total"].apply(classify_cholesterol)

# -------------------------------------
# Step 7: Save processed dataset
# -------------------------------------
output_dir = BASE_DIR / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "step1_cleaned_and_classified_dataset.csv"
df.to_csv(output_path, index=False)

print(f"\nCleaned & classified dataset saved to: {output_path}")
