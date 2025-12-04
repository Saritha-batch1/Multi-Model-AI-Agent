import pandas as pd

# Reference medical ranges (generic, can be improved)
REFERENCE_RANGES = {
    "hemoglobin": (12, 16),             # g/dL
    "platelet_count": (150000, 450000), # per µL
    "wbc_count": (4000, 11000),         # per µL
    "rbc_count": (4.0, 5.5),            # million/µL
    "mcv": (80, 100),                   # fL
    "mch": (27, 33),                    # pg
    "mchc": (32, 36),                   # g/dL
}

def validate_and_standardize(path, out_csv):
    df = pd.read_csv(path)

    issues = []

    for index, row in df.iterrows():
        row_issues = {}

        for param, (low, high) in REFERENCE_RANGES.items():
            value = row[param]  # <-- FIXED (uses correct column names)

            # Missing values
            if pd.isna(value):
                row_issues[param] = "Missing value"
                continue

            # Non-numeric values
            try:
                v = float(value)
            except ValueError:
                row_issues[param] = f"Invalid value: {value}"
                continue

            # Range validation
            if not (low <= v <= high):
                row_issues[param] = f"Out of normal range: {v}"

        if row_issues:
            issues.append({"row": index, "issues": row_issues})

    # Save validation results
    issues_df = pd.DataFrame(issues)
    issues_df.to_csv(out_csv, index=False)

    print(f"✅ Validation complete. Found {len(issues)} problematic records.")
    print(f"📁 Validation report saved to: {out_csv}")

if __name__ == "__main__":
    validate_and_standardize(
        "extracted_parameters.csv",
        "validation_report.csv"
    )
