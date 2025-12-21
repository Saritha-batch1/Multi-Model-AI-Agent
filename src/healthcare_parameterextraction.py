import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "merged_healthcare_data.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "healthcare_blood_parameters.csv")

# Load data
df = pd.read_csv(INPUT_PATH,low_memory=False)

# List of blood parameters present as columns
blood_parameters = {
    "Hemoglobin": "g/dl",
    "Rbc": "million/cumm",
    "Wbc": "cells/cumm",
    "Glucose": "mg/dl",
    "Creatinine": "mg/dl",
    "Cholesterol": "mg/dl",
    "Ast": "u/l",
    "Alt": "u/l",
    "Troponin": "ng/ml",
    "Lipase": "u/l",
    "Spirometry": "liters"
}

rows = []

# Convert wide format → long format
for idx, row in df.iterrows():
    for param, unit in blood_parameters.items():
        if param in df.columns and pd.notna(row[param]):
            rows.append({
                "row_id": idx,
                "parameter": param,
                "value": row[param],
                "unit": unit
            })

# Create DataFrame
result_df = pd.DataFrame(rows)

# Save output
result_df.to_csv(OUTPUT_PATH, index=False)

print("✅ Healthcare blood parameters extracted successfully")
print(f"📁 Saved to: {OUTPUT_PATH}")
print("\nSample output:")
print(result_df.head())