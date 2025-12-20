import pandas as pd

def generate_final_report():
    df = pd.read_csv("personalized_recommendations_report.csv")

    df["System_Conclusion"] = (
        "Health risks identified using a multi-model AI approach"
    )

    df["Disclaimer"] = (
        "This system is for educational purposes only and does not replace professional medical diagnosis."
    )

    df.to_csv("final_health_report.csv", index=False)
    print("✅ Final health report generated: final_health_report.csv")


if __name__ == "__main__":
    generate_final_report()
