import pandas as pd

def llm_like_response(patient_data, question):
    """
    Simulated LLM response using prompt-style reasoning.
    (Used when real LLM API is not available)
    """

    response = f"""
Based on the patient's blood report:

Hemoglobin: {patient_data.get('hemoglobin')}
WBC Count: {patient_data.get('wbc_count')}
Platelet Count: {patient_data.get('platelet_count')}

Question: {question}

Medical Explanation:
"""

    if patient_data.get("hemoglobin", 15) < 12:
        response += "- Hemoglobin is low, which may indicate anemia.\n"

    if patient_data.get("wbc_count", 7000) > 11000:
        response += "- WBC count is high, suggesting possible infection.\n"

    if patient_data.get("platelet_count", 200000) < 150000:
        response += "- Platelet count is low, increasing bleeding risk.\n"

    response += "\nPlease consult a doctor for professional advice."

    return response


if __name__ == "__main__":
    df = pd.read_csv("medical_diagnosis_report.csv")

    sample_patient = df.iloc[0].to_dict()
    question = "What does my blood report indicate?"

    answer = llm_like_response(sample_patient, question)
    print("🧠 LLM-style Medical Assistant Response:\n")
    print(answer)
