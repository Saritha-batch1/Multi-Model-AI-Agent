import pandas as pd
import re
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "ocr_cleaned_text.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "ocr_blood_parameters.csv")

df = pd.read_csv(INPUT_PATH)

print("Rows in OCR cleaned file:", len(df))
print("Columns:", df.columns)

results = []

# Flexible patterns (IMPORTANT)
patterns = {
    "crp": r"(crp|c\s*reactive\s*protein)[^0-9]*?(\d+(?:\.\d+)?)\s*(mg\s*/?\s*l)?",
    "hemoglobin": r"(hemoglobin|hb|hgb)[^0-9]*?(\d+(?:\.\d+)?)\s*(g\s*/?\s*d[l1])?",
    "wbc": r"(wbc|white\s*blood\s*cell|leukocytes)[^0-9]*?([\d,]+)\s*(cells\s*/?\s*cumm)?",
    "platelet": r"(platelet|plt)[^0-9]*?([\d,]+)",
    "glucose": r"(glucose|glu)[^0-9]*?(\d+(?:\.\d+)?)\s*(m[gq]\s*/?\s*d[l1])?",
    "creatinine": r"(creatinine|creat)[^0-9]*?(\d+(?:\.\d+)?)\s*(m[gq]\s*/?\s*d[l1])?"
}

# Loop
for _, row in df.iterrows():
    text = str(row["clean_text"])
    image = row.get("image_name", "unknown")

    for param, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            value = match.group(2).replace(",", "")
            unit = match.group(3) if len(match.groups()) >= 3 else ""

            results.append({
                "image_name": image,
                "parameter": param,
                "value": float(value),
                "unit": unit.strip() if unit else ""
            })

# Save results
result_df = pd.DataFrame(results)
print("Extracted rows:", len(result_df))

result_df.to_csv(OUTPUT_PATH, index=False)
print("✅ OCR parameter extraction completed")
print("Saved to:", OUTPUT_PATH)
print(result_df.head())