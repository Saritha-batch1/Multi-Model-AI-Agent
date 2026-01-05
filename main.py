import os

from Week1.text_extraction import extract_text
from Week1.parameters_extraction import extract_parameters, save_to_csv
from Week2.validation_standardization import (
    validate_and_standardize,
    save_validation_to_csv
)
from Week2.Parameter_Interpretation import interpret_parameters
from Week3.Pattern_Recognition import (
    pattern_risk_assessment,
    save_pattern_risk_to_csv
)
from Week4.Risk_Assessment import (
    assess_overall_risk,
    save_risk_assessment_to_csv
)
from Week5.findings_synthesis import synthesize_findings


def save_text(text: str, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    folder_path = input("Enter folder path containing reports: ").strip()

    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return

    # Output folders
    os.makedirs("outputs/text", exist_ok=True)

    files = sorted(os.listdir(folder_path))
    print(f"\nProcessing {len(files)} files...\n")

    for idx, filename in enumerate(files, start=1):
        file_path = os.path.join(folder_path, filename)
        patient_id = str(idx)

        try:
            print(f"Processing {filename} → Patient ID: {patient_id}")

            # -------- Task 1: Text Extraction --------
            text = extract_text(file_path)
            save_text(text, f"outputs/text/{patient_id}_extracted.txt")

            # -------- Task 2: Parameter Extraction --------
            parameters = extract_parameters(text)
            save_to_csv(patient_id, parameters)

            # -------- Task 3: Validation & Standardization --------
            validated = validate_and_standardize(parameters)
            save_validation_to_csv(patient_id, validated)

            # -------- Model 1: Parameter Interpretation --------
            interpret_parameters(validated)

            # -------- Model 2: Pattern Recognition --------
            model2_result = pattern_risk_assessment(validated)
            save_pattern_risk_to_csv(patient_id, model2_result)

            # -------- Model 4: Risk Assessment --------
            risk_result = assess_overall_risk(validated, model2_result)
            save_risk_assessment_to_csv(patient_id, risk_result)

        except Exception as e:
            print(f"Failed {filename}: {e}")

    # -------- Week 5: Findings Synthesis (RUN ONCE) --------
    synthesize_findings(
        validated_csv="outputs/validated_parameters.csv",
        pattern_csv="outputs/model2/pattern_risk_scores.csv",
        risk_csv="outputs/model4/final_risk_assessment.csv",
        output_path="outputs/week5/findings_summary.json"
    )

    print("\nBatch pipeline completed successfully")


if __name__ == "__main__":
    main()