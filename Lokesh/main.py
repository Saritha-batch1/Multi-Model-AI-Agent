import os
from Week1.text_extraction import extract_text
from Week1.parameters_extraction import extract_parameters, save_to_csv
from Week2.validation_standardization import (
    validate_and_standardize,
    save_validation_to_csv
)

def save_text(text: str, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    folder_path = input("Enter folder path containing reports: ").strip()

    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return

    os.makedirs("outputs/text", exist_ok=True)

    
    files = sorted(
        os.listdir(folder_path),
        key=lambda x: int(os.path.splitext(x)[0])
    )

    print(f"\n Processing {len(files)} files...\n")

    for filename in files:
        patient_id = os.path.splitext(filename)[0]  # "1", "2", "3"
        file_path = os.path.join(folder_path, filename)

        try:
            print(f"➡ Processing {filename} → Patient ID: {patient_id}")

            # -------- Task 1: Text Extraction --------
            text = extract_text(file_path)
            save_text(text, f"outputs/text/{patient_id}_extracted.txt")

            # -------- Task 2: Parameter Extraction --------
            parameters = extract_parameters(text)
            save_to_csv(patient_id, parameters)

            # -------- Task 3: Validation & Standardization --------
            validated_data = validate_and_standardize(parameters)
            save_validation_to_csv(patient_id, validated_data)

        except Exception as e:
            print(f"⚠ Failed {filename}: {e}")

    print("\n Batch pipeline completed successfully")

if __name__ == "__main__":
    main()
