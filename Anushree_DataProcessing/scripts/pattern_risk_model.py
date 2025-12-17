import pandas as pd

def assess_risk(row):
    risks = []

    # Anemia risk (pattern-based)
    if row["hemoglobin"] < 11 and row["rbc_count"] < 4:
        risks.append("High Anemia Risk")
    elif row["hemoglobin"] < 12:
        risks.append("Moderate Anemia Risk")

    # Infection risk
    if row["wbc_count"] > 11000:
        risks.append("Infection Risk")

    # Bleeding risk
    if row["platelet_count"] < 150000:
        risks.append("Bleeding Risk")

    if not risks:
        return "Low Risk"
    return "; ".join(risks)


def run_pattern_risk_model(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df["risk_assessment"] = df.apply(assess_risk, axis=1)
    df.to_csv(output_csv, index=False)
    print(f"✅ Model-2 risk report generated: {output_csv}")


if __name__ == "__main__":
    run_pattern_risk_model(
        "extracted_parameters.csv",
        "risk_assessment_report.csv"
    )
