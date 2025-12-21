import pandas as pd
import os
import re


# Paths

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "merged_healthcare_data.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "healthcare_text_analysis.csv")


# Load data

df = pd.read_csv(INPUT_PATH, low_memory=False)


# Text columns to analyze

TEXT_COLUMNS = [
    "Gender",
    "Blood Type",
    "Medical Condition",
    "Admission Type",
    "Medication",
    "Test Results",
    "Disease"
]


# Text cleaning function

def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Apply cleaning
for col in TEXT_COLUMNS:
    if col in df.columns:
        df[col + "_clean"] = df[col].apply(clean_text)


# Frequency analysis
analysis_results = []

for col in TEXT_COLUMNS:
    clean_col = col + "_clean"
    if clean_col in df.columns:
        top_values = df[clean_col].value_counts().head(5)
        for value, count in top_values.items():
            analysis_results.append({
                "column": col,
                "value": value,
                "count": count
            })


# Save results
analysis_df = pd.DataFrame(analysis_results)
analysis_df.to_csv(OUTPUT_PATH, index=False)

print("✅ Healthcare text analysis completed")
print(analysis_df.head())