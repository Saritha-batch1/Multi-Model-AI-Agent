import pandas as pd

def generate_recommendation(row):
    recommendations = []

    patterns = row.get("Detected_Patterns", "")
    context = row.get("Contextual_Insights", "")

    # Anemia-related advice
    if "Anemia" in patterns:
        recommendations.append(
            "Increase intake of iron-rich foods such as spinach, dates, and legumes"
        )
        recommendations.append(
            "Consult a healthcare professional for further evaluation of anemia"
        )

    # Infection-related advice
    if "Infection" in patterns:
        recommendations.append(
            "Monitor symptoms like fever, weakness, or fatigue"
        )
        recommendations.append(
            "Seek medical consultation if symptoms persist"
        )

    # Bleeding risk advice
    if "Bleeding Risk" in patterns:
        recommendations.append(
            "Avoid strenuous activities and prevent injuries"
        )
        recommendations.append(
            "Consult a doctor immediately if unusual bleeding is observed"
        )

    # Age-related general advice
    if isinstance(context, str) and "age" in context.lower():
        recommendations.append(
            "Regular health monitoring is recommended due to age-related risk factors"
        )

    # Default advice
    if not recommendations:
        return "Maintain a balanced diet and a healthy lifestyle"

    return "; ".join(recommendations)


def run_recommendation_generator(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df["Personalized_Recommendations"] = df.apply(
        generate_recommendation, axis=1
    )

    df.to_csv(output_csv, index=False)
    print(f"✅ Personalized recommendations generated: {output_csv}")


if __name__ == "__main__":
    run_recommendation_generator(
        "contextual_risk_report.csv",
        "personalized_recommendations_report.csv"
    )
