import pandas as pd

def generate_explanation(diagnosis_text):
    explanation = ""

    if "Anemia" in diagnosis_text:
        explanation += "Your hemoglobin level is low, which suggests anemia. You may feel tired or weak. Consider iron-rich foods.\n"

    if "Infection" in diagnosis_text:
        explanation += "Your white blood cell count is high, which indicates your body may be fighting an infection.\n"

    if "Thrombocytopenia" in diagnosis_text:
        explanation += "Your platelet count is low. This may increase bruising or bleeding risk.\n"

    if "Iron Deficiency" in diagnosis_text:
        explanation += "Your RBC level is low, suggesting possible iron deficiency. Eating iron-rich food may help.\n"

    if "B12" in diagnosis_text:
        explanation += "Your MCV value is high, which may indicate Vitamin B12 or folate deficiency.\n"

    if "Hypochromia" in diagnosis_text:
        explanation += "Your MCHC level is low, which may relate to anemia or low hemoglobin concentration.\n"

    if explanation.strip() == "":
        explanation = "Your blood parameters appear normal. No abnormalities detected."

    return explanation.strip()


def create_ai_explanation(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df["ai_explanation"] = df["diagnosis"].apply(generate_explanation)
    df.to_csv(output_csv, index=False)
    print(f"✨ AI explanation report saved to: {output_csv}")


if __name__ == "__main__":
    create_ai_explanation(
        "medical_diagnosis_report.csv",
        "ai_explanation_report.csv"
    )
