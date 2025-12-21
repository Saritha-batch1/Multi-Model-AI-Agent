import pandas as pd

def assess_risk(row):
    risks = []
    severity = "Low"

    # Anemia pattern
    if row["hemoglobin"] < 11 and row["rbc_count"] < 4:
        risks.append("Anemia")
        severity = "High"
    elif row["hemoglobin"] < 12:
        risks.append("Mild Anemia")
        severity = "Medium"

    # Infection pattern
    if row["wbc_count"] > 11000:
        risks.append("Possible Infection")
        severity = max(severity, "Medium")

    # Platelet-related risk
    if row["platelet_count"] < 150000:
        risks.append("Bleeding Risk")
        severity = "High"

    if not risks:
        return pd.Series(["No Significant Risk", "Low"])

    return pd.Series([", ".join(risks), severity])


def run_model_2(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df[["Detected_Patterns", "Risk_Level"]] = df.apply(
        assess_risk, axis=1
    )

    df.to_csv(output_csv, index=False)
    print(f"✅ Model 2 completed. Output saved to {output_csv}")


if __name__ == "__main__":
    run_model_2(
        "extracted_parameters.csv",
        "risk_assessment_report.csv"
    )
