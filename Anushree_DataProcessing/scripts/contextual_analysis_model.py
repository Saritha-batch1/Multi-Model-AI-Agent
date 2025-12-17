import pandas as pd

def apply_context(row):
    context_notes = []

    # Gender-based adjustment
    if row["gender"].lower() == "female" and row["hemoglobin"] < 12:
        context_notes.append("Hemoglobin slightly low for female")
    elif row["gender"].lower() == "male" and row["hemoglobin"] < 13:
        context_notes.append("Hemoglobin low for male")

    # Age-based adjustment
    if row["age"] > 60 and row["wbc_count"] > 10000:
        context_notes.append("Elevated infection risk due to age")

    if not context_notes:
        return "No additional context risk"

    return "; ".join(context_notes)


def run_model_3(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df["Contextual_Insights"] = df.apply(apply_context, axis=1)
    df.to_csv(output_csv, index=False)
    print(f"✅ Model 3 completed. Output saved to {output_csv}")


if __name__ == "__main__":
    run_model_3(
        "risk_assessment_report.csv",
        "contextual_risk_report.csv"
    )
