import pandas as pd

def extract_parameter_values(path, out_csv):
    df = pd.read_csv(path)

    extracted_data = []

    for index, row in df.iterrows():
        entry = {
            "age": row["Age"],
            "gender": row["Gender"],
            "hemoglobin": row["Hemoglobin"],
            "platelet_count": row["Platelet_Count"],         # FIXED
            "wbc_count": row["White_Blood_Cells"],           # FIXED
            "rbc_count": row["Red_Blood_Cells"],             # FIXED
            "mcv": row["MCV"],
            "mch": row["MCH"],
            "mchc": row["MCHC"]
        }
        extracted_data.append(entry)

    out_df = pd.DataFrame(extracted_data)
    out_df.to_csv(out_csv, index=False)

    print("Extracted key parameters for", len(extracted_data), "records.")
    print("Saved to:", out_csv)

if __name__ == "__main__":
    extract_parameter_values("blood_count_dataset.csv", "extracted_parameters.csv")
