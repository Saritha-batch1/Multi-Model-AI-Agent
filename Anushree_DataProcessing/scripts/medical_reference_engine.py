import pandas as pd

def diagnose_record(row):
    diagnosis = []

    # Hemoglobin
    if row["hemoglobin"] < 12:
        diagnosis.append("Low Hemoglobin — Possible Anemia")

    # WBC
    if row["wbc_count"] > 11000:
        diagnosis.append("High WBC — Possible Infection")
    elif row["wbc_count"] < 4000:
        diagnosis.append("Low WBC — Leukopenia risk")

    # Platelets
    if row["platelet_count"] < 150000:
        diagnosis.append("Low Platelets — Thrombocytopenia risk")

    # RBC
    if row["rbc_count"] < 4.0:
        diagnosis.append("Low RBC — Possible Iron Deficiency")

    # MCV
    if row["mcv"] > 100:
        diagnosis.append("High MCV — Possible B12/Folate Deficiency")
    elif row["mcv"] < 80:
        diagnosis.append("Low MCV — Microcytosis (possible iron deficiency)")

    # MCHC
    if row["mchc"] < 32:
        diagnosis.append("Low MCHC — Hypochromia")

    if not diagnosis:
        diagnosis.append("Normal — No abnormalities detected")

    return "; ".join(diagnosis)


def generate_medical_report(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df["diagnosis"] = df.apply(diagnose_record, axis=1)
    df.to_csv(output_csv, index=False)

    print(f"🩺 Medical report generated and saved to: {output_csv}")


if __name__ == "__main__":
    generate_medical_report(
        "extracted_parameters.csv",
        "medical_diagnosis_report.csv"
    )
