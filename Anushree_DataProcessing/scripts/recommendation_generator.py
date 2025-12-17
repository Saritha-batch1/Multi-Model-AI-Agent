import pandas as pd

def generate_recommendation(row):
    advice = []

    patterns = row["Detected_Patterns"]
    context = row["Contextual_Insights"]

    # Anemia recommendations
    if "Anemia" in patterns:
        advice.append("Increase intake of iron-rich foods (spinach, dates, legumes)")
        advice.append("Consult a physician for anemia evaluation")

    # Infection recommendations
    if "Infection" in patterns:
        advice.append("Monitor symptoms such as fever or fatigue")
        advice.append("Seek medical consultation if symptoms persist")

    # Bleeding risk recommendations
    if "Bleeding Risk" in patterns:
        advice.append("Avoid injuries and strenuous activities")
        advice.append("Consult a doctor immediately if bleeding occurs")

    # Age-related advice
    if "age" in context.lower():
        advice.append("Regular health monitoring is advised due to age")

    if not advice:
        return "Maintain a balanced diet and healthy lifestyle"

    return "; ".join(advice)


def run_recommendation_engine(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df["Personalized_Recommendations"] = df.apply(generate_recommendation, axis=1)
    df.to_csv(output_csv, index=False)
    print(f"✅ Recommendations generated and saved to {output_csv}")


if __name__ == "__main__":
    run_recommendation_engine(
        "contextual_risk_report.csv",
        "personalized_recommendations_report.csv"
    )
